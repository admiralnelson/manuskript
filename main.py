import sys
import lexer
sys.path.append("libs/lark")
import lark

RESERVED = 'RESERVED'
LPARANTHESE = "LPARANTHESE"
RPARANTHESE = "RPARANTHESE"
LSQBRACKET = "LSQBRACKET"
RSQBRACKET = "RSQBRACKET"
INTEGER      = 'INTEGER'
FIXED      = 'FIXED'
ID       = 'ID'
NEWLINE = "NEWLINE"
NUMERIC = "NUMERIC"
REGISTER = "REGISTER"
COMMA = "COMMA"
COLON = "COLON"

BOOLEAN = "BOOLEAN"
COMPARATOR = "COMPARATOR"
FLOW = "FLOW"
LOOP = "LOOP"

ASSIGN = "ASSIGN"
MINUS = "MINUS"

PROCEDURE = "PROCEDURE"

token_exprs = [
    (r'[ \t]+',              None),
    (r'[\n]',              NEWLINE),
    (r'#[^\n]*',               NEWLINE),
    (r'\=',                   ASSIGN),
    (r'\:',                   COLON),
    (r'\(',                    LPARANTHESE),
    (r'\)',                    RPARANTHESE),
    (r'\+',                    RESERVED),
    (r'-',                     MINUS),
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
    (r"true",                  RESERVED), 
    (r"false",                  RESERVED),
    (r'to',                 RESERVED),
    (r'for',                 RESERVED),
    (r'procedure',                 PROCEDURE),
    (r'ProcedureCall',                 RESERVED),
    (r'reg[0-9]+',                 REGISTER),
   #(r'[0-9]+',                INTEGER),
    (r'\d+\.?\d*',                 NUMERIC),
    (r'{',                    RESERVED),
    (r'}',                   RESERVED),    
    (r',',                   COMMA),    
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

    (r'[A-Za-z][A-Za-z0-9_]*', ID),
]

def isAlgebraBeginPrecheck(token):
    return token[1] == ASSIGN or token[1] == LPARANTHESE or token[1] == LSQBRACKET

def isAlgebraBegin(token):
    return token[1] == INTEGER or token[1] == FIXED or token[1] == MINUS or token[1] == ID

def isAlgebraEnd(token):
    return token[1] == BOOLEAN or  token[1] ==  COMPARATOR or token[1] == FLOW or  token[1] == LOOP or token[1] == LSQBRACKET or token[1] == RSQBRACKET or token[1] == NEWLINE

def isProcedureDeclaration(token):
    return token[1] == PROCEDURE and nextElement(token, tokens)[1] == ID and nextElement(nextElement(token,tokens),tokens)[1] == LPARANTHESE 

def isProcedureParamsEmpty(token):
    return token[1] == LPARANTHESE and nextElement(token, tokens)[1] == RPARANTHESE

def parseProcedureParams(token):
    data = tokens[:]  
    data = data[tokens.index(("(", LPARANTHESE)):tokens.index((")", RPARANTHESE))]
    data.pop(0)
    for d in data:
        if d[1] == COMMA or d[1] == COLON:
            data.pop(data.index(d))
    return data

def MBLex(characters):
    return lexer.lex(characters, token_exprs)

def peek(stack):
    return stack[-1] if stack else None

def nextElement(item, lists):
    return lists[lists.index(item)+1] if lists[lists.index(item)+1] else None

filename = "test1.txt"
file = open(filename)
characters = file.read()
file.close()
tokens = MBLex(characters)
p = []
i = 1
line = 1
algebraic = False
checkIfAlgebraic = True
procedure  = False
algebraicList = []
ProcedureList = []
for token in tokens:
    i = i + len(token[0])
    if(token[1] == NEWLINE) : 
        line = line + 1
        i = 0
        algebraic = False
        checkIfAlgebraic = True
        del algebraicList[:]

    #parse procedure declaration begin
    if(isProcedureDeclaration(token)):
        print "PROCEDURE"
        procedure = True
        ProcedureList.append(["Procedure"])
    if(procedure):
            procedure = False
            ProcedureList[ProcedureList.index(["Procedure"])].append(parseProcedureParams(token))
    #parse Algebraic expression
    if(isAlgebraBeginPrecheck(token) and checkIfAlgebraic):
        if(isAlgebraBegin(nextElement(token, tokens)) and checkIfAlgebraic):
            algebraic = True
            print "NUMBER WILL BEGIN"
            checkIfAlgebraic = False
            procedure = False

    elif(isAlgebraEnd(token) and checkIfAlgebraic):
        algebraic = False
        print "NUMBER ENDS"
        checkIfAlgebraic = True

    if(algebraic): algebraicList.append(token)
    
    #parse Algebraic expression end

    if(token[1] == LPARANTHESE): p.append(token)
    if(token[1] == RPARANTHESE): 
        if(len(p)>0):
            p.pop() 
        else:
            print("brackets didn't match!, there are more rbrackets than lbrackets at: '" + str(token[0]) + "' around char: " + str(i) + " line: " + str(line))
            break
    print str(token)+ "," + " " + str(len(token[0]))

if(len(p) != 0) :
    print("brackets didn't match!, there are more lbrackets than rbrackets at: '" + str(token[0]) + "' around char: " + str(i) + " line: " + str(line))

print(ProcedureList)
