Everything Search Syntax Compact (with Examples)
Operators: space=AND (ex: cat dog), |=OR (ex: cat|dog), !=NOT (ex: !cat), <>=Group (ex: <cat dog>), ""=Exact Phrase (ex: "cat dog").
Wildcards: * = 0+ chars (ex: *.txt), ? = 1 char (ex: ?.doc). (Whole filename match unless disabled).
Modifiers (prefix terms/functions):
ascii/utf8/noascii: (ex: ascii:test) (ASCII case),
case/nocase: (ex: case:ABC) (case match),
diacritics/nodiacritics: (ex: diacritics:cafe) (accent match),
file/files/nofileonly: (ex: file:) (file only),
folder/folders/nofolderonly: (ex: folder:) (folder only),
path/nopath: (ex: path:c:\test\file.txt) (full path),
regex/noregex: (ex: regex:^[a-z]+$)(regex),
wfn/wholefilename/nowfn/nowholefilename/exact: (ex: wfn:test) (whole filename),
wholeword/ww/nowholeword/noww: (ex: ww:word)(whole word),
wildcards/nowildcards: (ex: wildcards:*.txt) (wildcards).
Functions: function:value (=) (ex: size:1mb), <= (ex: size:<=10kb), < (ex: size:<1gb), > (ex: size:>5mb), >= (ex: size:>=2gb), start..end/start-end (range) (ex: size:1mb..5mb).
Size Syntax: size[kb|mb|gb] (ex: size:2gb). Size Constants: empty (ex: size:empty), tiny (ex: size:tiny), small (ex: size:small), medium (ex: size:medium), large (ex: size:large), huge (ex: size:huge), gigantic (ex: size:gigantic), unknown (ex: size:unknown).
Date Syntax: year (ex: 2023), month/year (ex: 12/2023), day/month/year (ex: 25/12/2023) (locale dep). YYYY[-MM[-DD[Thh[:mm[:ss[.sss]]]]]] (ex: 2023-12-25T10:30:00), YYYYMM[DD[Thh[mm[ss[.sss]]]]] (ex: 202312251030). Date Constants: today (ex: dm:today), yesterday (ex: dm:yesterday), last/past/prev/current/this/coming/next <year/month/week> (ex: dm:lastweek), last/past/prev/coming/next <x><years/months/weeks> (ex: dm:last2months), last/past/prev/coming/next <x><hours/minutes/mins/seconds/secs> (ex: dc:next10mins), Month/day names (ex: dm:december), unknown (ex: dc:unknown).
Attribute Constants: A (ex: attrib:A), C (ex: attrib:C), D (ex: attrib:D), E (ex: attrib:E), H (ex: attrib:H), I (ex: attrib:I), L (ex: attrib:L), N (ex: attrib:N), O (ex: attrib:O),P (ex: attrib:P), R (ex: attrib:R), S (ex: attrib:S), T (ex: attrib:T), V (ex: attrib:V).
Search Options: (Status bar toggle) Case (ex: case:abc), Whole Words (ex: wholeword:test), Path (ex: path:), Diacritics (ex: diacritics:cafe), Regex (ex: regex:). Filters: Everything (ex: everything:), Audio (ex: audio:), Compressed (ex: compressed:), Document (ex: doc:), Executable (ex: exe:), Folder (ex: folder:), Picture (ex: pic:), Video (ex: video:).
Advanced Search: Dialog for building complex searches (Search Menu).
Content Searching: (Slow). content:<text> (ex: content:findme) (iFilter or UTF-8). ansicontent: (ex: ansicontent:test), utf8content: (ex: utf8content:unicode), utf16content: (ex: utf16content:text), utf16becontent: (ex: utf16becontent:text). (Combine with other filters). Example: *.eml dm:thisweek content:banana.
ID3/FLAC tag search: track: (ex: track:5), year: (ex: year:2000), title: (ex: title:song), artist: (ex: artist:band), album: (ex: album:name), comment: (ex: comment:test), genre: (ex: genre:rock). (Slow, combine).
Image Search: width:<width> (ex: width:1000), height:<height> (ex: height:600), dimensions:<width>x<height> (ex: dimensions:1920x1080), orientation:<type>(ex: orientation:landscape) , bitdepth:<bitdepth> (ex: bitdepth:24). (Slow, combine, jpg/png/gif/bmp only).
Duplicate Files: dupe: (ex: dupe:*.mp3), attribdupe: (ex: attribdupe:), dadupe: (ex: dadupe:), dcdupe: (ex: dcdupe:), dmdupe: (ex: dmdupe:), namepartdupe: (ex: namepartdupe:), sizedupe: (ex: sizedupe:). (Entire index, sort by dupe type. Guide only).
Regex: regex: (ex: regex:^file[0-9]*\.txt$) (overrides other syntax). Must escape | and space in regex with double quotes.
Regex elements: a|b, (a|e), ., [abc], [^abc], [a-z], [a-zA-Z], ^, $, *, ?, +, {x}, {x,}, {x,y}, \.
Limit Results: count:number (ex: count:100).