## Localization tools for ExHibit (aka retouch/sketch) game system

### Usage

- `dump_key.py`: Dump two keys from game. Needs frida/psutil to be installed.
- `crypt_rld.py`: Use key to encrypt or decrypt RLD file. `key_def.bin` is for `def.rld` only, while `key.bin` is for other files.
- `patcher.py`: Patch RLD/RNF file for EN/CN i18n mode. Change `I18N` option in `ExHIBIT.ini` first.
- `textedit.py`: Extract and reinsert text from RLD file. It is recommended to apply patch on the file before you extract the text.
- `template/`: Contains translated version of resource files.

### License

This project is licensed under WTFPL.
