import metasequoia_java as ms_java

if __name__ == "__main__":
    # parse statement
    code = "try (Rt rt = new Rt()) {} catch ( Exception1 | Exception2 e ) {} finally {}"
    print(ms_java.JavaParser(ms_java.LexicalFSM(code)).parse_statement())

    # parse expression
    code = "name += (3 + 5) * 6"
    print(ms_java.JavaParser(ms_java.LexicalFSM(code)).parse_expression())

    # parse type
    code = "List<String>"
    print(ms_java.JavaParser(ms_java.LexicalFSM(code), mode=ms_java.ParserMode.TYPE).parse_type())
