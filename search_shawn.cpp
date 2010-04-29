///
/// working in ProcessPostings() and line 260
///

// Accumulators for ranking
// ≥ı ºªØDictionary
Accum = {}

// Accumulators reversed to put in order of relevancy
Rank = {}

// Offsets and length of each posting (in words), number of terms in index.
PostingOffset = 0
PostingLength = 0

NumTerms = ''

// Offsets, length in words of each document, and number of documents.
DocOffset, DocWordCount, NumDocs = 0

// Array of terms, type of Char
Term = []

// Doc IDs
DocID = [];

// Paths to data files
IndexFile = ''
SubIndexFile = ''
DocIndexFile = ''


// Loads the document index, which is of the form:
// <NumEntries><DocIDS><DocOffsets><DocLengths>
def LoadDocIndex(docindex)
    try:
        fileDocIndex = open(docindex, 'rb')
    except Exception:
        print('Error opening doc-index file \'%s\'!\n', docindex)
        sys.exit(1)

    NumDocs = fileDocIndex.read(1)

    // Read docids NOTE: 15 is number of bytes in docid + '\0'
    // TODO: check how many bytes are for wiki corpus docids
    char *A = (char*)malloc(sizeof(char) * NumDocs * 15);
    A = fileDocIndex.read(NumDocs*15)

    DocID = []

    // Extract docids
    k=1;
    len = NumDocs * 15;
    DocID[0] = A[0];
    i = 1
    while(i<len):
        if (A[i-1] == '\0'):
            DocID[k] = &A[i]
            k++;
        i++

    // Read DocOffsets
    DocOffset = fileDocIndex.read(NumDocs)

    // Read document word counts
    DocWordCount = (unsigned*)malloc(sizeof(unsigned) * NumDocs);

    fileDocIndex.close()


// Loads the subindex, the postings file
def LoadSubIndex(subindex)
    try:
        fileSubIndex = open(subindex, 'rb')
    except Exception:
        print('Error opening sub-index file \'%s\'!\n', subindex)
        sys.exit(1)

    int len=0
    TermList = []

    NumTerms = fileSubIndex.read(1)

    // Offset of each posting
    PostingOffset = fileSubIndex.read(NumTerms)

    // Length of each posting in bytes
    PostingLength = fileSubIndex.read(NumTerms)

    // Number of bytes in the posting terms array
    len = fileSubIndex.read(1)

    TermList = fileSubIndex.read(len)


    k=1
    Term[0] = TermList[0];
    i=0
    while i<len:
        if (TermList[i-1] == '\0'):
            Term[k] = TermList[i]
            k++;
        i++

    fileSubIndex.close()



// Locates the index of a term in the postings index.
def binsearch(term):
    hi=NumTerms+1
    lo=-1
    probe=0

    while (hi - lo > 1):
      probe = (hi + lo) / 2
      if (strcmp(Term[probe], term) < 0):
        lo = probe
      else:
        hi = probe
    
    if (strcmp(Term[hi],term) != 0):
      return -1
    else:
      return hi




// Add the postings to the accumulators, using tf.idf.
def ProcessPostings(A):
    T = []
    len=0
    d=0, f=0, o=0
    p = A.split()
    sscanf(p, "%s", T) // Just to be sure...
    p = strtok(0, " ")
    sscanf(p, "%d", &len)
    p = strtok(0, " ")

    idf = NumDocs / len
    tf=0.0
    while (p != 0 && len > 0):
        sscanf(p, "%d", &d)
        p = strtok(0, " ")

        sscanf(p, "%d", &f)
        p = strtok(0, " ")

        d += o
        tf = (double)f / (double)DocWordCount[d]

        Accum[d] += tf * idf
        o = d
        len--



// Loads the data filenames from the file 'search.param'.
def LoadDataFile() {
    try:
        dataFile = open('search.param', 'r');
    except Exception:
        print('Can\'t open \'search.param\' file for reading.\n Make sure search.param is in the same directory you\'re running from')
        sys.exit(1)

    SubIndexFile = dataFile.readline()
    DocIndexFile = dataFile.readline()
    IndexFile = dataFile.readline()

    dataFile.close()
}

def main(argv):
    // Max length of a query term in characters.
    MaxTermSize=30
    // Max number of bytes in a posting.
    MaxPostingSize=30000
    // Array for storing terms read in. Expands.
    D = []
    // Array for storing postings read in. Expands.
    P = []
    index=0, querynum=0
    
    // Load data	
    LoadDataFile();
    LoadSubIndex(SubIndexFile);
    LoadDocIndex(DocIndexFile);


    // Open postings
    try:
        filePostings = open(IndexFile, 'rb')
    except Exception:
        print('Can\'t open postings file \'%s\' for input, failing\n', IndexFile)
        sys.exit(1)

    // We can handle queries now...
    c=0, ch=0;
    while (1) {
    //printf("Enter query: ");
    // Get query number
    querynumber = raw_input("Enter querynumber:")
    if (1 != querynum) {
      break;
    }

    // Clean our structures for each query
    Accum.clear();
    Rank.clear();

    c=0;
    while (1):
        ch = raw_input("Enter Query:")
        // Make sure we can fit query in buffer
        if (c > MaxTermSize):
          //MaxTermSize *= 2
          D = []

        // Ignore Andrew's evil MSDOS end of line chars...
        if (ch == '\r'):
            continue;

        // Captured a complete query term, get and process postings.
        if (ch == ' ' || ch == '\n'):
            D[c] = '\0'
            // Term is now in D
            index = binsearch(D)
            if (index < 0):
                // Term not in index, ignore.
                c=0
                continue


            filePostings.seek(PostingOffset[index], os.SEEK_SET)

            // Make sure we can fit the positngs in memory
            while (PostingLength[index] > MaxPostingSize):
                MaxPostingSize = (int)((double)MaxPostingSize * 2);
                P = [];
    
            // Read the postings
            filePostings.read(PostingLength[index])

            P[PostingLength[index]] = '\0'

            // Posting is now in P
            ProcessPostings(P)

            c = 0
            if (ch == '\n'):
                break
            else:
                D[c] = ch;
                c++;
    // end while getting query

    // Reverse map so traversal is in order of relevancy
    // This is kind of like heap sort... Almost O(lg(n))...
    map<unsigned,double>::iterator itr = Accum.begin();
    double r=0.0;
    while (itr != Accum.end()) {
      // This is so that if two documents *happen* to have the
      // same rank, the second inserted doesn't overwrite the first.
      // This is due to the way that STL maps are implemented...
      r = itr->second;
      while (Rank[r] != 0)
        r *= 0.99;
      Rank[r] = itr->first;
      itr++;
    }
    // Traverse and print out search results.
    map<double,unsigned>::reverse_iterator ritr = Rank.rbegin();
    while (ritr != Rank.rend()) {
      printf("%d X %s X %lg X\n",
        querynum, DocID[ritr->second], ritr->first);
      ritr++;
    }

  } // while input

  free(PostingOffset);
  free(PostingLength);
  free(DocOffset);
  free(DocWordCount);
  free(DocID[0]);
  free(Term[0]);

  return 0;
}