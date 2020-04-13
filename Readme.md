# PyPraat

A  [praat](http://www.fon.hum.uva.nl/praat) like keyword clipping python tool  for short audio wav.
---------------------

## Requirement

```
      sudo apt-get install libasound-dev
      pip install -r requirements.txt
```

## Features

    *  pratt UI like；
    *  output pratt compatible textgrid files；
    *  can browse and operate many audio files in a list widget smoothly.
    *  convinient clipping operations thanks to the hot keys；
    *  support total operation history .

## Hot Keys

    *   space  : confirm and go to next item；
    *   f/p/Tab : play audio；
    *   b : go to last item；
    *   s : add a new time interval edge；
    *   d : delete a time interval； 
    *   r  : backtrack an operation .
    *   a  : bypass/ undo bypass.

## To Do

    *   enhance robustness when parsing directory and textgrid files;
    *   accelerate real time displaying of playing progress line；
