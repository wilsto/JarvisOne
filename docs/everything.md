# Everything Search Syntax Guide

## Extension Search

### Using ext: (Recommended)

- Single extension:
  ✓ Correct: `ext:pdf` (finds all PDF files)
  ✓ Correct: `ext:doc` (finds all DOC files)
  ✗ Incorrect: `*.pdf` (wildcard is less efficient)

- Multiple extensions:
  ✓ Correct: `ext:doc;docx;pdf` (finds DOC, DOCX, and PDF files)
  ✓ Correct: `ext:py;pyw;ipynb dm:today` (today's Python files)
  ✗ Incorrect: `*.py|*.pyw|*.ipynb` (avoid using multiple wildcards)
  ✗ Incorrect: `ext:py | ext:pyw` (don't use | with ext:)

### Extension Examples

- Documents: `ext:doc;docx;pdf;txt`
- Images: `ext:jpg;jpeg;png;gif`
- Python: `ext:py;pyw;ipynb`
- Web: `ext:html;htm;css;js`
- Archives: `ext:zip;rar;7z`

### Combining with Other Modifiers

✓ Correct: `ext:doc;docx dm:lastweek size:<1mb` (Word files from last week under 1MB)
✓ Correct: `ext:py;pyw dm:today path:c:\projects` (today's Python files in projects)
✗ Incorrect: `*.doc|*.docx dm:lastweek` (avoid using wildcards and |)

## Basic Search Operators

- AND: Use space between terms
  ✓ Correct: `cat dog` (finds files containing both "cat" AND "dog")
  ✗ Incorrect: `cat AND dog` (word "AND" doesn't work)

- OR: Use | (pipe) between EACH term (no spaces around |)
  ✓ Correct: `report|memo|note` (finds files containing any of these words)
  ✗ Incorrect: `report OR memo OR note` (word "OR" doesn't work)
  ✗ Incorrect: `report | memo` (spaces around | break the query)

- NOT: Use ! before term (no space after !)
  ✓ Correct: `!cat` (finds files NOT containing "cat")
  ✗ Incorrect: `NOT cat` (word "NOT" doesn't work)
  ✗ Incorrect: `! cat` (space after ! breaks the query)

- Grouping: Use <> to group terms (no spaces around <>)
  ✓ Correct: `<cat dog>` (groups "cat dog" together)
  ✗ Incorrect: `< cat dog >` (spaces around <> break the query)

- Exact Phrase: Use quotes "" (no spaces around "")
  ✓ Correct: `"cat dog"` (finds exact phrase "cat dog")
  ✗ Incorrect: `" cat dog "` (spaces around quotes are included in search)

## Wildcards

- - = Zero or more characters
  ✓ Correct: `*.txt` (finds all .txt files)
  ✓ Correct: `test*.txt` (finds test1.txt, testing.txt, etc.)
  ✗ Incorrect: `* .txt` (space after * breaks the query)

- ? = Single character
  ✓ Correct: `?.doc` (finds a.doc, b.doc, etc.)
  ✓ Correct: `test?.txt` (finds test1.txt, testA.txt, etc.)
  ✗ Incorrect: `? .doc` (space after ? breaks the query)

## Search Modifiers

### Case Sensitivity

- case: Match case exactly
  ✓ Correct: `case:ABC` (matches ABC exactly)
  ✓ Correct: `case:"Test File"` (matches "Test File" exactly)
  ✗ Incorrect: `case: ABC` (space after : breaks the query)

- nocase: Ignore case
  ✓ Correct: `nocase:test` (matches TEST, Test, test)
  ✗ Incorrect: `nocase: test` (space after : breaks the query)

### Path Options

- file: Search files only
  ✓ Correct: `file: *.txt` (only show .txt files)
  ✓ Correct: `file:` (show all files)

- folder: Search folders only
  ✓ Correct: `folder: test` (only show folders containing "test")
  ✓ Correct: `folder:` (show all folders)

- path: Search full path
  ✓ Correct: `path:c:\test\file.txt` (match full path)
  ✓ Correct: `path:"c:\my documents"` (use quotes for paths with spaces)
  ✗ Incorrect: `path: c:\test` (space after : breaks the query)

## Size Search

### Size Functions

- Exact size:
  ✓ Correct: `size:1mb` (exactly 1MB)
  ✗ Incorrect: `size: 1mb` (space after : breaks the query)

- Less than or equal:
  ✓ Correct: `size:<=10kb` (10KB or less)
  ✗ Incorrect: `size:<= 10kb` (space after <= breaks the query)

- Greater than:
  ✓ Correct: `size:>5mb` (more than 5MB)
  ✗ Incorrect: `size: >5mb` (space after : breaks the query)

- Range:
  ✓ Correct: `size:1mb..5mb` (between 1MB and 5MB)
  ✗ Incorrect: `size:1mb .. 5mb` (spaces around .. break the query)

### Size Constants

- empty
- tiny
- small
- medium
- large
- huge
- gigantic

## Date Search

### Date Keywords

- Today:
  ✓ Correct: `dm:today` (files from today)
  ✓ Correct: `dm:today *.doc|*.docx` (today's Word files)
  ✗ Incorrect: `dm: today` (space after : breaks the query)

- Time ranges:
  ✓ Correct: `dm:lastweek` (last week's files)
  ✓ Correct: `dc:last2hours *.log` (log files from last 2 hours)
  ✗ Incorrect: `dm:last week` (space breaks the query)

### Date Formats

- Year: `2023`
- Month/Year: `12/2023`
- Full date: `25/12/2023`
- ISO format: `2023-12-25T10:30:00`

### Date Comparisons

- Before a date:
  ✓ Correct: `dm:<2023-01-01` (files before 2023)
  ✓ Correct: `dm:<"01/01/2023"` (files before January 1, 2023)
  ✗ Incorrect: `dm: <2023-01-01` (space after : breaks the query)

- After a date:
  ✓ Correct: `dm:>2023-06-30` (files after June 30, 2023)
  ✓ Correct: `dm:>"30/06/2023"` (files after June 30, 2023)
  ✗ Incorrect: `dm:> 2023-06-30` (space after > breaks the query)

- Date range:
  ✓ Correct: `dm:2023-01-01..2023-12-31` (files from 2023)
  ✓ Correct: `dm:"01/01/2023".."31/12/2023"` (files from 2023)
  ✗ Incorrect: `dm:2023-01-01 .. 2023-12-31` (spaces around .. break the query)

### Combining Searches

✓ Correct: `dm:today size:>1mb *.doc|*.docx` (today's Word files > 1MB)
✓ Correct: `path:c:\projects dm:lastweek *.py|*.pyw` (last week's Python files in projects)
✗ Incorrect: `*.doc|*.docx dm:today size:>1mb` (modifiers should come first)

## Best Practices

1. Start with broad searches, then refine with modifiers
2. Use quotes for exact matches and paths with spaces
3. Combine size and date filters for more precise results
4. Use wildcards carefully as they can slow down searches
5. General Rules:
   - No spaces after : in modifiers
   - No spaces around operators (|, !, <>, ..)
   - Use quotes for terms containing spaces
   - Use ^ to escape \, &, |, >, < and ^
   - Prefer ext: over wildcards for file types
   - Use semicolons (;) to separate multiple extensions

## File Attributes

- A: Archive
- H: Hidden
- R: Read-only
- S: System
- C: Compressed
- E: Encrypted

## Content Type Filters

- everything: All files
- audio: Audio files
- doc: Documents
- exe: Executables
- pic: Pictures
- compressed: Compressed files

## Common File Types and Extensions

### Documents

✓ Correct: `ext:doc;docx;pdf;txt;rtf` (all document types)
✓ Correct: `ext:doc;docx dm:today` (today's Word files)
✗ Incorrect: `*.doc|*.docx` (avoid wildcards)

### Images

✓ Correct: `ext:jpg;jpeg;png;gif;bmp` (all image types)
✓ Correct: `ext:jpg;png size:>1mb` (large images)
✗ Incorrect: `*.jpg|*.png|*.gif` (avoid wildcards)

### Code Files

✓ Correct: `ext:py;pyw;ipynb` (Python files)
✓ Correct: `ext:js;ts;jsx;tsx` (JavaScript/TypeScript)
✗ Incorrect: `*.py OR *.pyw` (avoid OR operator)

### Audio/Video

✓ Correct: `ext:mp3;wav;flac;m4a` (audio files)
✓ Correct: `ext:mp4;avi;mkv;mov` (video files)
✗ Incorrect: `*.mp3|*.wav` (avoid wildcards)

### Archives

✓ Correct: `ext:zip;rar;7z;tar;gz` (compressed files)
✓ Correct: `ext:zip;rar size:>100mb` (large archives)
✗ Incorrect: `*.zip OR *.rar` (avoid OR operator)

### Web Files

✓ Correct: `ext:html;htm;css;js` (web files)
✓ Correct: `ext:php;asp;jsp` (server scripts)
✗ Incorrect: `*.html|*.htm` (avoid wildcards)

### Development

✓ Correct: `ext:c;cpp;h;hpp` (C/C++ files)
✓ Correct: `ext:java;class;jar` (Java files)
✗ Incorrect: `*.cpp|*.h` (avoid wildcards)

### Database

✓ Correct: `ext:sql;db;sqlite` (database files)
✓ Correct: `ext:mdb;accdb` (Access databases)
✗ Incorrect: `*.sql|*.db` (avoid wildcards)

### Office Documents

✓ Correct: `ext:doc;docx;xls;xlsx;ppt;pptx` (all Office files)
✓ Correct: `ext:xls;xlsx dm:today` (today's Excel files)
✗ Incorrect: `*.doc|*.docx` (avoid wildcards)

### Scripts

✓ Correct: `ext:ps1;bat;cmd;sh` (script files)
✓ Correct: `ext:ps1;bat dm:lastweek` (recent scripts)
✗ Incorrect: `*.bat|*.cmd` (avoid wildcards)

## Common Search Patterns

### File Types

✓ Correct: `ext:doc;docx;pdf dm:today` (today's documents)
✓ Correct: `ext:jpg;png size:>1mb` (large images)
✗ Incorrect: `*.jpg|*.png|*.gif` (avoid wildcards and |)

### Advanced Combinations

✓ Correct: `ext:doc;docx dm:lastweek size:<1mb` (small Word files from last week)
✓ Correct: `ext:py;pyw dm:today path:c:\projects size:>0` (non-empty Python files)
✗ Incorrect: `*.py OR *.pyw dm:today` (avoid OR and wildcards)
