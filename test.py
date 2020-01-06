    # This example implements a LOGO-like toy language for Python's turtle, with interpreter.

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass

import turtle
import random
from lark import Lark,  Transformer, v_args
from lark.tree import pydot__tree_to_png

reservedKeywords = [
        "procedure",
        "Number",
        "Boolean",
        "if",
        "else",
        "true",
        "false",
        "die",
        "return",
        "bgroup"
        "paren"
    ]

IF_STATE = 0
ELSEIF_STATE =1 
ELSE_STATE = 2

def isNumber(s):
    try:
        int(str(s))
        return True
    except ValueError:
        return False

def isBooleanLiteral(s):
    if s == "true" : return True
    if s == "false" : return True
    return False

def isVariable(s):
    if(str(s) == "true") : return False
    if(str(s) == "false") : return False
    try:
        int(str(s))
        return False
    except ValueError:
        return True

procedures = []
@v_args(inline=True) # Affects the signatures of the methods
class CalculateTree(Transformer):
    number = int

    def __init__(self):
        self.mathVars = [] # clear every assigment or expression check
        self.parentsLevel = 1 # clear every assigment  or expression check

        self.flag_if = IF_STATE

        self.vars = [] 
        self.literals = []
        
        self.blockLevel  =1 # clear every procedure
        self.output = "" # clear every procedure
        self.paramsdeclares = [] # clear every procedure
        
        self.blockcondition = "" # clear every block
        self.neg = False
    #def procedure(self, *args):
        #print "procedure " + str(args)

    ################################################  MATH OPERATIONS
    def op_add(self, args1, args2 = None):
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            args1 = "\"" + self.mathVars[-3] +  "\""
        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(store_add, \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2) + "),\n"

    def op_sub(self, args1, args2 = None):
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            args1 = "\"" + self.mathVars[-3] +  "\""
        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(store_sub, \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2)  + "),\n"

    def op_mul(self, args1, args2 = None):
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            if(isNumber(args2)):
                args1 = "\"" + self.mathVars[-1] +  "\""
            else:
                args1 = "\"" + self.mathVars[-2] +  "\""
            
        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(store_mul, \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2)  + "),\n"

    def op_minus(self, arg1):
        if(arg1 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
            self.mathVars.append(":paren" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "(store_mul, \"" +  self.mathVars[-1]  + "\", \"" +  self.mathVars[-2] + "\", " + str(-1)  + "),\n"
        else:
            self.mathVars.append(":paren" + str(self.parentsLevel))
            self.output += "\t"*self.blockLevel +  "(assign, \"" +  self.mathVars[-1]  + "\", 1),\n"
            self.output += "\t"*self.blockLevel +  "(val_mul, \"" +  self.mathVars[-1]  + "\", -" + str(arg1) + "),\n"
            
        

    def op_div(self, args1, args2 = None):
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            if(isNumber(args2)):
                args1 = "\"" + self.mathVars[-1] +  "\""
            else:
                args1 = "\"" + self.mathVars[-2] +  "\""
            
        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(store_div, \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2)  + "),\n"
    ################################################  MATH OPERATIONS END

    ################################################  COMPARATION OPERATIONS BEGIN


    ################################################  COMPARATION OPERATIONS END


    ################################################  BOOLEAN OPERATIONS BEGIN
    def op_or(self, args1, args2 = None):
        #args1 = str(args1)
        #args2 = str(args2)
        if(isBooleanLiteral(args1) and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- boolean1: "+ args1 +" or "+ args2  +"\n"
            a = 0
            b = 0
            if(args1 == "true"): a = 1
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,"+ str(a) +", " + str(b) +"),\n"
        elif(args1 == None and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- boolean2: "+ self.mathVars[-2] +" or "+ args2  +"\n"
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_or,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\"," + str(b) +"),\n"
        elif(args1 == None):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- boolean4 : "+ self.mathVars[-2] +" or "+ self.mathVars[0] +"\n"
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_or,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\", \"" + self.mathVars[0]  +"\"),\n"            
            
        else:
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            if(args2 == "true"): args2 = 1
            elif(args2 == "false"): args2 = 0
            else: args2 = "\":"+ args2 + "\""
            self.output += "\t"*self.blockLevel +  "# ---- boolean3: \":"+ args1 +"\" or "+ str(args2)  +"\n"
            self.output += "\t"*(self.blockLevel) +  "(store_or, \""+ self.mathVars[-1]  +"\", \":"+ args1  +"\", " + str(args2) +"),\n"
        #print str(args1) + " second args " + str(args2)

    def op_and(self, args1, args2 = None):
        #args1 = str(args1)
        #args2 = str(args2)
        if(isBooleanLiteral(args1) and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- boolean1: "+ args1 +" and "+ args2  +"\n"
            a = 0
            b = 0
            if(args1 == "true"): a = 1
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,"+ str(a) +", " + str(b) +"),\n"
        elif(args1 == None and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- boolean2: "+ self.mathVars[-2] +" and "+ args2  +"\n"
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\"," + str(b) +"),\n"
        elif(args1 == None):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- boolean4: "+ self.mathVars[-2] +" and "+ self.mathVars[-3] +"\n"
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\", \"" + self.mathVars[-3]  +"\"),\n"
            
            
        else:
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            if(args2 == "true"): args2 = 1
            elif(args2 == "false"): args2 = 0
            else: args2 = "\":"+ args2 + "\""
            self.output += "\t"*self.blockLevel +  "# ---- boolean3: \""+ args1 +"\" and "+ str(args2)  +"\n"
            self.output += "\t"*(self.blockLevel) +  "(store_and, \""+ self.mathVars[-1]  +"\", \":"+ args1  +"\", " + str(args2) +"),\n"
        #print str(args1) + " second args " + str(args2)

    def op_neq(self, arg1, arg2):        
        self.mathVars.append(":bgroup" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "# ---- boolean: "+ str(arg1) +" neq "+ str(arg2) +"\n"
        self.output += "\t"*self.blockLevel +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
        self.output += "\t"*self.blockLevel +  "(try_begin),\n"
        self.output += "\t"*((self.blockLevel)+1) +  "(neq," 
        if(isNumber(arg1)): self.output += str(arg1)
        else: self.output += "\"" + str(arg1) + "\""
        self.output += ","
        if(isNumber(arg2)): self.output += str(arg2)
        else: self.output += "\"" + str(arg2) + "\""
        self.output += "),\n"
        self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 1),\n"
        self.output += "\t"*self.blockLevel +  "(try_end),\n"
        self.output += "\t"*self.blockLevel +  "# ---- end ---\n"
          
        #raise Exception("OK")
    def op_neg(self, arg1):
        if(arg1 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- negation: "+ self.mathVars[-2]  +"\n"
            self.output += "\t"*(self.blockLevel) +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
            self.output += "\t"*self.blockLevel +  "(try_begin),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(eq, \"" +  self.mathVars[-2] + "\", 1),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
            self.output += "\t"*self.blockLevel +  "(try_else),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(eq, \"" +  self.mathVars[-2] + "\", 0),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 1),\n"
            self.output += "\t"*self.blockLevel +  "(try_end),\n"

        else:
            if(str(arg1) == "false") : arg1 = 0
            elif(str(arg1) == "true") : arg1 = 1
            else: arg1 = "\":" + arg1 + "\""
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.output += "\t"*self.blockLevel +  "# ---- negation: "+  str(arg1)   +"\n"
            self.output += "\t"*(self.blockLevel) +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
            self.output += "\t"*self.blockLevel +  "(try_begin),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(eq, " +  str(arg1) + ", 1),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
            self.output += "\t"*self.blockLevel +  "(try_else),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(eq, " +  str(arg1) + ", 0),\n"
            self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 1),\n"
            self.output += "\t"*self.blockLevel +  "(try_end),\n"


       # raise Exception("!")
    ################################################  BOOLEAN OPERATIONS END
    def expression(self, arg1=None):
        
        if(arg1 == None):
            arg1 = self.mathVars[-1]
        else:
            self.literals.append(arg1)
            #del self.mathVars[:]
            self.mathVars.pop()
        print("# expr " +  str(arg1))
    
    def assignment(self, arg1, arg2=None):
        vars = dict(self.vars)
        if(arg2==None):
            arg2 = self.mathVars[-1]
            #print(vars[":" + arg1])
            if(":" + arg1  in vars):
                self.output +=  "\t"*self.blockLevel  +  "(assign, \":" + arg1 + "\", \"" +  str(arg2) + "\"),\n"
            elif("$" + arg1  in vars):
                self.output +=  "\t"*self.blockLevel  +  "(assign, \"$" + arg1 + "\", \"" +  str(arg2) + "\"),\n"
            else:
                raise Exception( "COMPILER ERROR: undefined " + arg1 + " for local or global variable!")
            self.mathVars.pop()
            self.parentsLevel = 1
        else:
            del self.literals[:]
            if(":" + arg1  in vars):
                variable = vars[":"+arg1]  
            elif("$" + arg1  in vars):
                variable = vars["$"+arg1]
            else:
                raise Exception( "COMPILER ERROR: undefined " + arg1 + " for local or global variable!")
            if(str(type(arg2)) == "<class 'lark.tree.Tree'>"): 
                # FUNCTION
                print("TREE!")
            elif(isVariable(arg2)):
                if(":" + arg2  in vars):
                    arg2 = "\":" + arg2 + "\""
                elif("$" + arg2  in vars):
                    arg2 = "\"$" + arg2 + "\""
                else:
                    raise Exception( "COMPILER ERROR: assign " + str(arg1)  + " to undefined variable " + str(arg2) + "!")
                
            else:
                if(variable=="Boolean"):
                    if str(arg2) == "true":
                        self.output +=  "\t"*self.blockLevel+  "# "+ str(arg1) + " := true (1) " + "\n" 
                        arg2 = 1
                    elif str(arg2) == "false":
                        self.output +=  "\t"*self.blockLevel+  "# "+ str(arg1) + " := false (0) " + "\n" 
                        arg2 = 0
                    else: 
                        raise Exception( "COMPILER ERROR: " + arg1 + " is being assigned with incorrect data type. assigned value: " + str(arg2) + ", expect: boolean true or false ")
                    

                if(variable=="Number"):
                    try:
                        int(str(arg2))
                    except ValueError:
                        raise Exception( "COMPILER ERROR: " + arg1 + " is being assigned with incorrect data type. assigned value: " + str(arg2) + ", expect: Numeric ")
                    #invalid = arg2 != "true" or "false"
                    #if(invalid): raise Exception( "COMPILER ERROR: " + arg1 + " is being assigned with incorrect data type. assigned value: " + arg2 + " expect: boolean true or false ")

            
            matching = [s for s in vars if arg1 in s]
            self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + matching[0]  + "\", " +  str(arg2) + "),\n"

    def variabledeclare(self, arg1, arg2):
        if(arg1 in reservedKeywords):
            raise Exception("COMPILER ERROR: " + arg1 + " is reserved keyword!")
        vars = dict(self.vars)
        if( ":" + arg1 in vars or "$" + arg1 in vars ):
            raise Exception("COMPILER ERROR: " + arg1 + " is already defined!")

        self.output +=  "\t"*self.blockLevel+  "# var declare: "+ str(arg1) + " type :" + str(arg2)  + "\n"
        self.output +=  "\t"*self.blockLevel+ "(assign, \":" + str(arg1) + "\", 0),\n\n" 
        self.vars.append(( ":" + str(arg1), str(arg2)))

    def variabledeclareparams(self, arg1, arg2):
        if(arg1 in reservedKeywords):
            raise Exception("COMPILER ERROR: " + arg1 + " is reserved keyword!")
        self.output +=  "\t"*self.blockLevel+  "# var declare: "+ str(arg1) + " type :" + str(arg2)  + "\n" 
        self.vars.append(( ":" + str(arg1), str(arg2)))

    def variabledeclareglobal(self, arg1, arg2):
        self.output +=  "\t"*self.blockLevel + "# var declare: "+ str(arg1) + " type :" + str(arg2) + "\n"
        self.output +=  "\t"*self.blockLevel+ "(assign, \"$" + str(arg1) + "\", 0),\n\n" 
        self.vars.append(( "$" + str(arg1), str(arg2)))

    def block(self, *args):
        if(self.blockLevel == 1):
            print("# no tbe block")
        #self.blockLevel += 1
        #print "# block " + str(args)

    def if_block(self, *args):
        self.flag_if = IF_STATE
        self.parentsLevel = 1
        args = str(args[0])
        print(args)
        if(args  == "true"):
            self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, 1,1)"
        elif(args == "false"):
            self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, 1,0)"
        else:
            if(len(self.mathVars) ==0 ):self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, \""+ "FUCK" + str(args) + "\", 1)"
            else:
                self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, \""+ self.mathVars[-1]  + "\", 1)"
        self.output =  self.output.replace("@REPLACE", self.blockcondition)
        self.blockcondition = ""
        #del self.mathVars[:]

    def else_block(self, *args):
        self.flag_if = ELSE_STATE
        self.parentsLevel = 1
        args = str(args[0])
        print(args)
        if(args  == "true"):
            self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, 1,1)"
        elif(args == "false"):
            self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, 1,0)"
        else:
            if(len(self.mathVars) ==0 ):self.blockcondition = "\t"*((self.blockLevel)-2) +  "(eq, \""+ "FUCK" + str(args) + "\", 1)"
            else:
                self.blockcondition = "\t"*((self.blockLevel)-2) +  "(neq, \""+ self.mathVars[-1]  + "\", 1)"
        self.output =  self.output.replace("@REPLACE", self.blockcondition)
        self.blockcondition = ""
        del self.mathVars[:]

    def beginblock(self, *args):
        self.blockLevel += 1
        try_begin = "(try_begin)" if self.flag_if == IF_STATE else "(else_try)"
        self.output +=  "\t"*(self.blockLevel-1)+ try_begin +",\n" + "\t"*(self.blockLevel)+"@REPLACE,\n" 
        print("begin!")

    def endblock(self, *args):
        self.blockLevel -= 1
        self.output +=  "\t"*self.blockLevel+ "(try_end),\n\n" 
        print("begin!")


    def paramsdeclare(self, *args):
        self.output +=  "\t"*self.blockLevel + "#---parameter declarations begin---\n "
        if(len(args)!= 0):
            index = 0
            for i in  range(0, len(args)-1,2):
                index += 1
                variablename = str(args[i])
                variabletype = str(args[i+1])
                #print variablename + " " + variabletype
                self.variabledeclareparams(variablename ,variabletype)
                self.output += "\t"*self.blockLevel +  "(store_script_param, \":" +  str(args[i])  + "\", " + str(index)  + "),\n"
        else:
            print("# params declare: " + str(args))
        self.output +=  "\t"*self.blockLevel + "#---parameter declarations end---\n "


    def exitprocedure(self):
        self.output +=  "\t"*self.blockLevel + "(eq, 0, 1)"

    def procedure(self, *args):
        proc = "\t(\"" + str(args[1]) + "\",\n"
        proc += "\t[\n" + self.output  +"\n\t]"
        procedures.append(proc)
        self.blockLevel  =1 # clear every procedure
        self.output = "" # clear every procedure
        del self.paramsdeclares[:] # clear every procedure
        del self.vars[:] # clear every procedure
        print("# procedure" + str(args))




turtle_grammar = """
start: (procedure | function)+ 

?procedure: "procedure" procedurename paramsdeclare  mainblock
exitprocedure: "die"
?function: "function" procedurename paramsdeclare ":" returnsdeclare  mainblock

?procedurename: NAME

paramsdeclare : "("")"  
				| "(" NAME ":" TYPE ")" 
		        | "(" NAME ":" TYPE ("," NAME ":" TYPE)+ ")" 

returnsdeclare  :  "(" TYPE ")" 
		        | "("  TYPE (","  TYPE)+ ")" 

beginblock : "{"
endblock: "}"

mainblock :          "{""}"  
				| "{" (instruction)* "}" 

block: beginblock  (instruction)* endblock

?instruction: variable ";"
            | assignment ";"
            | variabledeclare ";"
            | exitprocedure ";"
            | ifstatement

?expression :  bool_or


        ?bool_or: bool_and 
            | bool_or  "||" bool_and -> op_or

        ?bool_and: comp
            | bool_and  "&&" comp -> op_and

        ?comp: sum
            | comp  "<" sum -> op_gt 
            | comp  ">" sum -> op_lt
		    | comp  "!=" sum -> op_neq

		?sum: product
			| sum "+" product -> op_add
			| sum "-" product -> op_sub

		?product: atom
			| product "*" atom -> op_mul
			| product "/" atom -> op_div

		?atom: NUMBER         -> number
			 | "-" atom       -> op_minus
			 | "(" expression ")"
             | variable
             | functionexpression





	?procedureexprssion: procedurename params
    ?functionexpression: procedurename params 
		?params:  "("")" 
			| "(" variable ")" 
			| "(" variable ("," variable)+ ")" 
			| "(" expression ")" 
			| "(" expression ("," expression)+ ")" 
	
     

?assignment: variable "=" expression
           | variabledeclare "=" expression 
//           | variabledeclare "=" STRING 
//           | variable "=" STRING 

ifstatement:  "if" "(" (expression | BOOL )  ")" block -> if_block
          | ifstatement ( "else if" "(" (expression | BOOL )  ")" block )+ -> elif_block
          | ifstatement ("else" block) -> else_block 


variabledeclareassign : NAME ":" TYPE ("=" expression) 
variabledeclare: NAME ":" TYPE 
variabledeclareglobal: "global" NAME ":" TYPE 
array: variable "[" sum "]"  

?variable : NAME


NAME: /[A-Za-z][A-Za-z0-9_]*/
NUMBER: /\d+\.?\d*/
STRING: /./
TYPE: "Number" | "String" | "QString" | "Procedure" | "Boolean"
    | "Faction" | "Presentation" | "Troop" | "Agent" | "Item"
BOOL: "true"
	| "false"


 %import common.WS
%ignore WS
"""

parser = Lark(turtle_grammar, parser='lalr', transformer=CalculateTree())



def main():
    while True:
        code = input('> ')
        try:
            run_turtle(code)
        except Exception as e:
            print(e)

def test():
    text = """
       procedure OpFaggot(faggottryPoints : Number)
       {
            bool1: Boolean; bool2: Boolean; bool3: Boolean; bool4: Boolean;


            if((bool1 || bool2) || (true && false) && (1 != 2))
            {
                faggottryPoints = -1;
            }
            else
            {
                faggottryPoints = 3;
            }
       }


       
    """
    
    tree = parser.parse(text)
    print(tree.pretty())
    print(str(procedures[0]))
    #pydot__tree_to_png(tree, "output.png")

if __name__ == '__main__':
    test()
    #main()