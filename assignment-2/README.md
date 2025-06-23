## Assignment 2

### Pi setup

#### Install system dependencies:

```
$ sudo apt update -y && sudo apt install -y iw tshark
```

### Capturing packets

`$ sudo ./capture.sh -i <capture network interface> [-f <capture filter>] [-o <capture to file>]`
