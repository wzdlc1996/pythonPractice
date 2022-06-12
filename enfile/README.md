# README

能够方便批量提取加密文件的小程序. 需要unrar的可执行文件, 也需要手动引入[rarfile](https://github.com/markokr/rarfile), 可以从Winrar的安装路径下获取. 项目目录应为:

```
.
├── bin
│   ├── unrar
│   └── unrar.exe
├── enfile_framework.spec
├── enfileMain.py
├── enfileMain.ui
├── enfileUtils.py
├── main.py
├── rarfile.py
└── README.md
```

## dependency:

1.  pikepdf==3.1.0
2.  msoffcrypto-tool==5.0.0
3.  pyzipper==0.3.5