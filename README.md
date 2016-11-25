# sms3

This package use to send SMS message for python 3.
The source code is modified from pythons sms package(author: Amos Latteier) within MIT licence.

## Usage
```python
    import sms3
    m = sms3.Modem('/dev/ttyUSB0')
    m.send('+886987026316', 'hello world')
```

## License
MIT
