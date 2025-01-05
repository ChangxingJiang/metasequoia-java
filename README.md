# metasequoia-java：水杉 Java 解析器

## 安装方法

```shell
pip install metasequoia-java
```

## 使用方法

解析语句：

```python
code = "try (Rt rt = new Rt()) {} catch ( Exception1 | Exception2 e ) {} finally {}"
print(ms_java.JavaParser(ms_java.LexicalFSM(code)).parse_statement())
```

解析表达式：

```python
# parse expression
code = "name += (3 + 5) * 6"
print(ms_java.JavaParser(ms_java.LexicalFSM(code)).parse_expression())
```

解析类型：

```python
# parse type
code = "List<String>"
print(ms_java.JavaParser(ms_java.LexicalFSM(code), mode=ms_java.ParserMode.TYPE).parse_type())
```

## 设计思路

与其他解析逻辑一样，我们采用词法解析与语法解析分离的解析器实现方案。

- 词法解析：将 Unicode 字符串转换为 Token 流
- 语法解析：将 Token 流转换为抽象语法树

在词法解析层，我们采用有限状态自动机实现；在语法解析层，我们采用调用的方式实现。

之所以在语法解析层采用调用的方式实现，主要是出于如下 5 个考虑：

- 与 JDK 文档一致，在开发时不需要将 JDK 文档的语法撰写为 LALR(1) 的语法，方便后续维护开发
- 与 JDK 的解析逻辑一致，避免因后续 JDK 版本出现类似 `non-sealed` 关键字等语法，导致需要再 LALR(1) 语法下新增更多复杂处理，降低后续维护难度
- 更容易地保证抽象语法树与 JDK 抽象语法树的一致性
- 虽然会损失一定的解析性能，但是可以通过 Python 性能优化器补偿，损失可以接受
- 存在 `>>` 等运算符，在实际使用时可能需要考虑拆开为多个 Token 解析的情况

项目结构如下：

- `ast`：抽象语法树节点及相关常量、函数等
- `grammar`：语法解析器
- `lexical`：词法解析器

终结符的设计思路：

- 在终结符类型的枚举类上，我们大体延用了 JDK 源码中的名称，但将驼峰式改为下划线式以适应 Python 的风格；
- 我们将每个终结符之后的空格、换行符和注释，作为该终结符的附属元素添加。

## 
