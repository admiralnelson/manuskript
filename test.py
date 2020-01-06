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

DEBUG = False

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
        self.else_if_counter = 0# pop element if if statment is terminated

        self.globals = []
        self.vars = [] 
        self.literals = []
        
        self.blockLevel  =1 # clear every procedure
        self.output = "" # clear every procedure
        self.paramsdeclares = [] # clear every procedure
        
        self.blockcondition = "" # clear every block
        self.neg = False
        self.enteredIfForIndent = False
        self.currentProcedureName = ""
    #def procedure(self, *args):
        #print "procedure " + str(args)

    ################################################  MATH OPERATIONS
    def op_add(self, args1, args2 = None):
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            args1 = "\"" + self.mathVars[-3] +  "\""
        if(isVariable(args2)):
            self.isValidVariable(args2)
        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(store_add, \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2) + "),\n"

    def op_sub(self, args1, args2 = None):
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
            arg2IsMathVar = True
        if(args1 == None):
            args1 = "\"" + self.mathVars[-3] +  "\""
        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(store_sub, \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2)  + "),\n"

    def op_mul(self, args1, args2 = None):
        arg2IsMathVar = False
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            if(isNumber(args2)):
                args1 = "\"" + self.mathVars[-1] +  "\""
                arg2IsMathVar = True
            else:
                args1 = "\"" + self.mathVars[-2] +  "\""

        if(not isNumber(args1)) :
            var = self.isValidVariable(args1)
            if(var[0][0] != "$"):
                args1 = "\"" + var[0] + "\"" if not arg2IsMathVar else args1 
            else:
                args1 = "\"" + var[0] + "\"" 
        if(not isNumber(args2)) : 
            if(not isVariable(args2)): raise Exception( "COMPILER ERROR: undefined " + args2 + " for local or global variable!")

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
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean1: "+ args1 +" or "+ args2  +"\n")
            a = 0
            b = 0
            if(args1 == "true"): a = 1
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,"+ str(a) +", " + str(b) +"),\n"
        elif(args1 == None and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean2: "+ self.mathVars[-2] +" or "+ args2  +"\n")
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_or,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\"," + str(b) +"),\n"
        elif(args1 == None):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean4 : "+ self.mathVars[-2] +" or "+ self.mathVars[0] +"\n")
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_or,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\", \"" + self.mathVars[0]  +"\"),\n"            
        elif(args1 != None and args2 == None):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            args2 =  self.mathVars[-2] 
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean5: \":"+ args1 +"\" or \""+ str(args2)  +"\" \n")
            self.output += "\t"*(self.blockLevel) +  "(store_or, \""+ self.mathVars[-1]  +"\", \":" + args1 + "\", \"" + args2  +"\" ),\n"
        else:
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            if(args2 == "true"): args2 = 1
            elif(args2 == "false"): args2 = 0
            else: args2 = "\":"+ args2 + "\""
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean3: \":"+ args1 +"\" or "+ str(args2)  +"\n")
            self.output += "\t"*(self.blockLevel) +  "(store_or, \""+ self.mathVars[-1]  +"\", \":"+ args1  +"\", " + str(args2) +"),\n"
        #print str(args1) + " second args " + str(args2)

    def op_and(self, args1, args2 = None):
        #args1 = str(args1)
        #args2 = str(args2)
        if(isBooleanLiteral(args1) and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean1: "+ args1 +" and "+ args2  +"\n")
            a = 0
            b = 0
            if(args1 == "true"): a = 1
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,"+ str(a) +", " + str(b) +"),\n"
        elif(args1 == None and isBooleanLiteral(args2)):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean2: "+ self.mathVars[-2] +" and "+ args2  +"\n")
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\"," + str(b) +"),\n"
        elif(args1 == None):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean4: "+ self.mathVars[-2] +" and "+ self.mathVars[-3] +"\n")
            b = 0
            if(args2 == "true"): b = 1
            self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\", \"" + self.mathVars[-3]  +"\"),\n"
        elif(args1 != None and args2 == None):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            args2 =  self.mathVars[-2] 
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean5: \":"+ args1 +"\" and \""+ str(args2)  +"\" \n")
            self.output += "\t"*(self.blockLevel) +  "(store_and, \""+ self.mathVars[-1]  +"\", \":" + args1 + "\", \"" + args2  +"\" ),\n"
        
        else:
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            if(args2 == "true"): args2 = 1
            elif(args2 == "false"): args2 = 0
            else: args2 = "\":"+ args2 + "\""
            self.append_comment("\t"*self.blockLevel +  "# ---- boolean3: \""+ args1 +"\" and "+ str(args2)  +"\n")
            self.output += "\t"*(self.blockLevel) +  "(store_and, \""+ self.mathVars[-1]  +"\", \":"+ args1  +"\", " + str(args2) +"),\n"
        #print str(args1) + " second args " + str(args2)

    def op_neq(self, arg1, arg2):        
        self.mathVars.append(":bgroup" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.append_comment("\t"*self.blockLevel +  "# ---- boolean: "+ str(arg1) +" neq "+ str(arg2) +"\n")
        self.output += "\t"*self.blockLevel +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
        self.output += "\t"*self.blockLevel +  "(try_begin),\n"
        self.output += "\t"*((self.blockLevel)+1) +  "(neq," 
        if(isNumber(arg1)): self.output += str(arg1)
        else: 
            if(str(arg1[0] != '$')):
                self.output += "\":" + str(arg1) + "\""
        
        self.output += ","

        if(isNumber(arg2)): self.output += str(arg2)
        else: 
            if(str(arg2[0] != '$')):
                self.output += "\":" + str(arg2) + "\""
        self.output += "),\n"
        self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 1),\n"
        self.output += "\t"*self.blockLevel +  "(try_end),\n"
        self.append_comment("\t"*self.blockLevel +  "# ---- end ---\n")
          
        #raise Exception("OK")
    def op_neg(self, arg1):
        if(arg1 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
            self.append_comment("\t"*self.blockLevel +  "# ---- negation1: "+ self.mathVars[-2]  +"\n")
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
            self.append_comment("\t"*self.blockLevel +  "# ---- negation2: "+  str(arg1)   +"\n")
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
            if(self.isValidVariable(arg1)):
                self.output +=  "\t"*self.blockLevel  +  "(assign, \":" + arg1 + "\", \"" +  str(arg2) + "\"),\n"            
            if(arg1[0] == "$"):
                if(self.isValidVariable(arg1)):
                    self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1 + "\", \"" +  str(arg2) + "\"),\n"
            
            self.mathVars.pop()
            self.parentsLevel = 1
        else:
            del self.literals[:]
            variable = self.isValidVariable(arg1)[1]
            if(str(type(arg2)) == "<class 'lark.tree.Tree'>"): 
                # FUNCTION
                print("TREE!")
            elif(isVariable(arg2)):
                self.isValidVariable(arg2)
                
            else:
                if(variable=="Boolean"):
                    if str(arg2) == "true":
                        self.append_comment("\t"*self.blockLevel+  "# "+ str(arg1) + " := true (1) " + "\n")
                        arg2 = 1
                    elif str(arg2) == "false":
                        self.append_comment("\t"*self.blockLevel+  "# "+ str(arg1) + " := false (0) " + "\n")
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
        if( ":" + arg1 in vars):
            raise Exception("COMPILER ERROR: " + arg1 + " is already defined!")
        
        for glob in self.globals:
            if(glob[0] == arg1):
                raise Exception("COMPILER ERROR: " + arg1 + " is already defined at " + glob[2] + " as " + glob[1] )
        
        if(str(arg1)[0] != "$"):
            self.append_comment("\t"*self.blockLevel+  "# var declare: "+ str(arg1) + " type :" + str(arg2)  + "\n")
            self.output +=  "\t"*self.blockLevel+ "(assign, \":" + str(arg1) + "\", 0),\n" 
            self.vars.append(( ":" + str(arg1), str(arg2)))
        else:
            self.append_comment("\t"*self.blockLevel+  "# var declare global: "+ str(arg1) + " type :" + str(arg2)  + "\n")
            self.output +=  "\t"*self.blockLevel+ "(assign, \""+ str(arg1) + "\", 0),\n" 
            self.globals.append(( str(arg1), str(arg2), self.currentProcedureName))

    def variabledeclareparams(self, arg1, arg2):
        if(arg1 in reservedKeywords):
            raise Exception("COMPILER ERROR: " + arg1 + " is reserved keyword!")
        self.append_comment("\t"*self.blockLevel+  "# var declare: "+ str(arg1) + " type :" + str(arg2)  + "\n" )
        self.vars.append(( ":" + str(arg1), str(arg2)))


    def block(self, *args):
        if(self.blockLevel == 1):
            print("# no tbe block")
        #self.blockLevel += 1
        #print "# block " + str(args)

    def test_expression(self, arg):
        if(arg == None and self.else_if_counter == 0):
            self.blockcondition = "\t"*(self.blockLevel ) + "(eq, \"" + self.mathVars[-1] + "\", 1), \n"
            self.enteredIfForIndent  = True
        elif(arg == None and self.else_if_counter > 0):
            self.blockcondition = "\t"*(self.blockLevel - 1) + "(eq, \"" + self.mathVars[-1] + "\", 1), \n"
        else:
            if arg == "true":
                self.blockcondition = "\t"*(self.blockLevel + 1) +  "(eq, 1,1), \n"
            elif arg == "false":
                self.blockcondition = "\t"*(self.blockLevel + 1) +  "(eq, 1,0), \n"
        del self.mathVars[:]

    def else_if_block(self, *args):
        pass

    def beginblock(self, *args):
        tabs = "\t"*(self.blockLevel) if (self.enteredIfForIndent) else ""
        self.blockLevel += 1       
        self.output +=  "\t"*(self.blockLevel-1)+ "(try_begin),\n" + tabs + self.blockcondition
        self.blockcondition = ""
        self.enteredIfForIndent = False
        print("begin!")

    def else_if_try(self, *args):
        self.else_if_counter += 1
        self.output +=  "\t"*(self.blockLevel-1)+ "(else_try),\n" + self.blockcondition
        self.blockcondition = ""
        print("else!")

    def else_try(self, *args):
        self.else_if_counter += 1
        self.output +=  "\t"*(self.blockLevel-1)+ "(else_try),\n" 
        print("else!")

    def endblock(self, *args):
        self.blockLevel -= 1
        self.output +=  "\t"*self.blockLevel+ "(try_end),\n\n" 
        print("begin!")

    def paramsdeclare(self, *args):
        self.append_comment("\t"*self.blockLevel + "#---parameter declarations begin---\n ")
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
        self.append_comment("\t"*self.blockLevel + "#---parameter declarations end---\n ")


    def exitprocedure(self):
        self.output +=  "\t"*self.blockLevel + "(eq, 0, 1)"

    def procedure(self, *args):
        self.currentProcedureName = str(args[0])
        proc = "(\"" + str(args[0]) + "\",[\n"
        proc += self.output 
        proc += "]),"
        procedures.append(proc)
        self.blockLevel  =1 # clear every procedure
        self.output = "" # clear every procedure
        del self.paramsdeclares[:] # clear every procedure
        del self.vars[:] # clear every procedure
        print("# procedure" + str(args))
    def procedure_name(self, arg1):
        self.currentProcedureName = str(arg1 )

    def isValidVariable(self, var):
        var = str(var)
        if(var[0] == "$"):
            for glob in self.globals:
                if var == glob[0]: return glob
            raise Exception( "COMPILER ERROR: undefined " + var + " for global variable at procedure: " + self.currentProcedureName)
        for v in self.vars:
            if(v[0] == ":" + var): return v
        for v in self.mathVars:
            if("\"" + v + "\"" == var): return v
            if( v == var): return v
        raise Exception( "COMPILER ERROR: undefined " + var + " for local variable at procedure: " + self.currentProcedureName)
        
    def append_comment(self, text):
        if(DEBUG):
            self.output += text



turtle_grammar = """
start: (procedure | function)+ 

?procedure: "procedure" procedurename paramsdeclare  mainblock
exitprocedure: "die"
?function: "function" procedurename paramsdeclare ":" returnsdeclare  mainblock

?procedurename: NAME -> procedure_name

paramsdeclare : "("")"  
				| "(" NAME ":" TYPE ")" 
		        | "(" NAME ":" TYPE ("," NAME ":" TYPE)+ ")" 

returnsdeclare  :  "(" TYPE ")" 
		        | "("  TYPE (","  TYPE)+ ")" 


mainblock :     "begin""end"  
				| "begin" (instruction)* "end" 

beginblock: "then"
endblock: "end"
else_if_try: "else" "if"
else_try: "else"

test : "(" (expression | BOOL ) ")" -> test_expression

ifstatement: if_body endblock 
            | if_body (try_else_if_body)+ (try_else_body)? endblock  -> else_if_block


if_body: "if" test beginblock (instruction)*
try_else_if_body : else_if_try test "then" (instruction)* 
try_else_body: else_try (instruction)* 
     
?instruction: assignment ";"
            | variabledeclare ";"
            | exitprocedure ";"
            | ifstatement

?expression :  bool_or
        ?bool_or: bool_and 
            | bool_or  "or" bool_and -> op_or

        ?bool_and: comp
            | bool_and  "and" comp -> op_and

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




variabledeclareassign : NAME ":" TYPE ("=" expression) 
variabledeclare: NAME ":" TYPE 
indexing: variable "[" sum "]"  

?variable : NAME


NAME: /\$?[A-Za-z][A-Za-z0-9_]*/
NUMBER: /\d+\.?\d*/
STRING: /./
TYPE: "Number" | "String" | "QString" | "Procedure" | "Boolean"
    | "Faction" | "Presentation" | "Troop" | "Agent" | "Item" | "Array" | "DynamicArray"
BOOL: "true"
	| "false"


 %import common.WS
%ignore WS
"""

parser = Lark(turtle_grammar, parser='lalr', transformer=CalculateTree(), debug=True)



def main():
    while True:
        code = input('> ')
        try:
            run_turtle(code)
        except Exception as e:
            print(e)

def test():
    text = """
       procedure CalculateFactionTension(RelationFacA : Number, RelationFacB: Number)
       begin
            bool1: Boolean; bool2: Boolean; bool3: Boolean; bool4: Boolean;
            array: Array;
            $GLOBAL: Number;
            if(
                (bool1 or bool2) or 
                (true and false) and (1 != 2)
              )
            then
                Number123: Number;
                RelationFacA = -1 + RelationFacB * (RelationFacA * -100) * 2 + $GLOBAL * 100;
                Number123 = RelationFacA;
                if(true) then
                    Number123  = 0;
                else if(Number123 != Number123) then
                    Number123 = 9999 - 00;
                end
            else if(bool2 or true and false) then
                RelationFacA = -0 + RelationFacB * (RelationFacA * -100) * 2;
            else 
                RelationFacB = -9999;
                RelationFacB = -(9999 + -100);
            end
       end


       
    """
    
    tree = parser.parse(text)
    print(tree.pretty())
    print(str(procedures[0]))
    #pydot__tree_to_png(tree, "output.png")

if __name__ == '__main__':
    test()
    #main()