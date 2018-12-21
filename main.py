import lexer

RESERVED = 'RESERVED'
INTEGER      = 'INTEGER'
ID       = 'ID'

token_exprs = [
    (r'[ \n\t]+',              None),
    (r'#[^\n]*',               None),
    (r'\=',                   RESERVED),
    (r'\:',                   RESERVED),
    (r'\(',                    RESERVED),
    (r'\)',                    RESERVED),
    (r'\+',                    RESERVED),
    (r'-',                     RESERVED),
    (r'\*',                    RESERVED),
    (r'/',                     RESERVED),
    (r'<=',                    RESERVED),
    (r'<',                     RESERVED),
    (r'>=',                    RESERVED),
    (r'>',                     RESERVED),
    (r'=',                     RESERVED),
    (r'!=',                    RESERVED),
    (r'and',                   RESERVED),
    (r'or',                    RESERVED),
    (r'not',                   RESERVED),
    (r'if',                    RESERVED),
    (r'then',                  RESERVED),
    (r'else',                  RESERVED),
    (r'to',                 RESERVED),
    (r'for',                 RESERVED),
    (r'procedure',                 RESERVED),
    (r'ProcedureCall',                 RESERVED),
    (r'reg[0-9]+',                 RESERVED),
    (r'{',                    RESERVED),
    (r'}',                   RESERVED),    
    (r',',                   RESERVED),    
    (r'Integer',             RESERVED),    
    (r'FixedPoint',             RESERVED),    
    (r'Position',             RESERVED),    
    (r'String',             RESERVED),    
    (r'Item',             RESERVED),   
    (r'Agent',             RESERVED),   
    (r'Troop',             RESERVED),   
    (r'Scene',             RESERVED),  
    (r'Party',             RESERVED),       
    (r'Faction',             RESERVED),    
    (r'GameMenu',             RESERVED),   
    (r'Presentation',             RESERVED),   
    (r'[0-9]+',                INTEGER),
    (r'[A-Za-z][A-Za-z0-9_]*', ID),
]

def MBLex(characters):
    return lexer.lex(characters, token_exprs)

filename = "test1.txt"
file = open(filename)
characters = file.read()
file.close()
tokens = MBLex(characters)
for token in tokens:
    print token