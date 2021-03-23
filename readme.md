##  加密密码本


#### 演示

![演示](https://raw.githubusercontent.com/prgrmz01/pass_pad/master/demo.gif)

#### install

```shell
pip install pass_pad
```

#### 说明
> 启动时, x.csv.enc -> x.csv -> x.db, 
然后 命令提示符 -> 命令 -> sql -> x.db

> 退出时, x.db -> x.csv -> x.csv.enc, 
并 删除 x.db, x.csv, 随后 可以提交 x.csv.enc到git了

#### TODO
> x.db 放到 内存文件系统中
