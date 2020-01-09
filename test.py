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
        "function",
        "result",
        "Number",
        "Boolean",
        "if",
        "else",
        "then",
        "true",
        "false",
        "die",
        "return",
        "bgroup",
        "paren",
        "funcRet",
        "begin",
        "end",
        "or",
        "and",
        "not",
        
    ]

DEBUG = True

BOOLEAN = 1
NUMBER = 2

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

def ConvertBooleanLiteralToNumeric(s):
    if s == "true" : return 1
    if s == "false" : return 0

def ElementContainsNone(l):
    j = 0
    for i in l:
        j += 1
        if(i == None): return j
    return False

def IsLocalVariable(s):
    return s[0] != "$"

def DecorateWithQuotes(s):
    if(s[0] != "\"" and s[1] != "$"): return s
    if(s[0] != "\""): return s
    return "\""  + s  + "\"" 

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
        self.returnTypes = []   # clear every procedure
        self.loopEndIterators = []  # clear every procedure

        self.blockcondition = "" # clear every block        
        self.returnRegCounter = 0 # clear every procedure
        self.neg = False
        self.enteredIf = False # clear every procedure
        self.enteredLoop = False
        self.currentProcedureName = ""
        self.lastVariableNameDeclared = () # clear every assigment
        self.lastAssignedVariable = ()  # clear every assigment
        self.lastAssignedValue = 0
        self.assignMultipleValueFromFunc = [] # clear every assigment
        self.proceduresName = []
        

        self.advanceIndexInProcessFuncCall = 0 # will be incremented at op_process_func_call and reset at assigment
    def op_proc_call(self, arg, *args):
        var = self.isValidVariable(arg)
        self.output += "\t"*self.blockLevel +  "(call_script, \"" +  str(var[0])  + "\", " + str(args)  + " ),\n"

    def op_func_call(self, arg, args):
        procedureSign = self.FindProcedureOrFunction(arg)
        paramSign =  []
        returnSign = []
        if(procedureSign == None):
            raise Exception("proc not found")
        elif(procedureSign[0] == self.currentProcedureName):
            paramSign  = self.paramsdeclares
            returnSign  = self.returnTypes
        else:
            paramSign =  procedureSign[1]
            returnSign = procedureSign[2]

        if(len(paramSign) != len(args.children)):
            raise Exception("unmatched param sign")
        if(len(returnSign ) == 0):
            raise Exception("is a procedure")
        if(len(returnSign ) > 1):
            raise Exception("function returns multiple result")

        self.output += "\t"*self.blockLevel +  "(call_script, \"script_" +  str(arg)  + "\""

        j = 0

        mathVars = []
        params = []
        for param in args.children:
            if(param == None):                
               #self.mathVars.sort(reverse  = True)
                var = self.mathVars[-1]
                var = self.isValidVariable(var)
                self.mathVars.pop()
                
                if(paramSign[j][1] != var[1]):
                   raise Exception("unmatched param sign 2")
                #self.output += ", " + "\"" + str(var[0]) + "\""
                mathVars.append(var[0])
                params.append(None)
            else:
                var = self.isValidVariable(param)
                if(var):
                    if(paramSign[j][1] != var[1]):
                        raise Exception("unmatched param sign 3")
                    params.append(var[0])
                    #self.output += ", " + "\"" + str(var[0]) + "\""
                else:
                    #
                    params.append(str(param))
                    #self.output += ", " +  str(param)  
            
            j += 1
        i = 0
        mathVars.sort(reverse = True)
        for v in params:
            if (v != None):
                var = self.isValidVariable(v)
                if(var):
                    self.output += ", " + "\"" + str(var[0]) + "\""
                else:
                    self.output += ", " + str(v) 
            else:
                if(len(mathVars) > 0 ):
                    v = mathVars.pop()
                    self.output += ", " + "\"" + str(v) + "\""

        self.output += "),\n"

        if(returnSign[0] == "Number"):
            self.mathVars.append(":paren" + str(self.parentsLevel) )
            self.parentsLevel += 1
        elif(returnSign[0] == "Boolean"):
            self.mathVars.append(":bgroup" + str(self.parentsLevel))
            self.parentsLevel += 1
        elif(returnSign[0] == "Array"):
            self.mathVars.append(":tarray" + str(self.parentsLevel) )
            self.parentsLevel += 1
        #self.mathVars.sort(reverse = True)

        self.output += "\t"*self.blockLevel  + "(assign,\""+  self.mathVars[-1] +"\", reg0),\n"
        
        #self.mathVars.pop()
        
    def op_func_call_mult_return(self, arg, args):
        procedureSign = self.FindProcedureOrFunction(arg)
        paramSign =  []
        returnSign = []
        if(procedureSign == None):
            raise Exception("proc not found")
        elif(procedureSign[0] == self.currentProcedureName):
            paramSign  = self.paramsdeclares
            returnSign  = self.returnTypes
        else:
            paramSign =  procedureSign[1]
            returnSign = procedureSign[2]

        if(len(paramSign) != len(args.children)):
            raise Exception("unmatched param sign")
        if(len(returnSign ) == 0):
            raise Exception("is a procedure")
        #if(len(returnSign ) > 1):
        #    raise Exception("function returns multiple result")

        self.output += "\t"*self.blockLevel +  "(call_script, \"script_" +  str(arg)  + "\""

        j = 0

        mathVars = []
        params = []
        for param in args.children:
            if(param == None):                
               #self.mathVars.sort(reverse  = True)
                var = self.mathVars[-1]
                var = self.isValidVariable(var)
                self.mathVars.pop()
                
                if(paramSign[j][1] != var[1]):
                   raise Exception("unmatched param sign 2")
                #self.output += ", " + "\"" + str(var[0]) + "\""
                mathVars.append(var[0])
                params.append(None)
            else:
                var = self.isValidVariable(param)
                if(var):
                    if(paramSign[j][1] != var[1]):
                        raise Exception("unmatched param sign 3")
                    params.append(var[0])
                    #self.output += ", " + "\"" + str(var[0]) + "\""
                else:
                    #
                    params.append(str(param))
                    #self.output += ", " +  str(param)  
            
            j += 1
        i = 0
        mathVars.sort(reverse = True)
        for v in params:
            if (v != None):
                var = self.isValidVariable(v)
                if(var):
                    self.output += ", " + "\"" + str(var[0]) + "\""
                else:
                    self.output += ", " + str(v) 
            else:
                if(len(mathVars) > 0 ):
                    v = mathVars.pop()
                    self.output += ", " + "\"" + str(v) + "\""

        self.output += "),\n"

        i = 0
        for ret in returnSign:
            if(ret == "Number"):
                self.mathVars.append(":paren" + str(self.parentsLevel) )
                self.parentsLevel += 1
            elif(ret == "Boolean"):
                self.mathVars.append(":bgroup" + str(self.parentsLevel))
                self.parentsLevel += 1
            elif(ret == "Array"):
                self.mathVars.append(":tarray" + str(self.parentsLevel) )
                self.parentsLevel += 1
            self.output += "\t"*self.blockLevel  + "(assign,\""+  self.mathVars[-1 * i] +"\", reg"+ str(i) +"),\n"
            i += 1
        
        
        
    ################################################  MATH OPERATIONS
    def op_add_sub(self, args1, args2 = None, op = "store_add"):
        appendAssign = False
        if(args2 == None):
            args2 = "\"" + self.mathVars[-1] +  "\""
        if(args1 == None):
            if(len(self.mathVars) > 2):
                args1 = "\"" + self.mathVars[-3] +  "\""
            elif(len(self.mathVars) == 1):
                args1 = "\"" + self.mathVars[-1] +  "\""
            else:
                args1 = "\"" + self.mathVars[-2] +  "\""


        if(isNumber(args2)):
            args2 = str(args2)
        elif(IsLocalVariable(args2)):
            args2 = "\"" + self.isValidVariable(args2)[0] + "\""
        else:
            self.isValidVariable(args2)
            args2 = "\"" + args2 + "\""
        
        if(isNumber(args1)):
            args1 = str(args1)
        elif(IsLocalVariable(args1)):
            args1 = "\"" + self.isValidVariable(args1)[0] + "\""
        else:
            self.isValidVariable(args1)
            args1 = "\"" + args1 + "\""
            appendAssign = True

        self.mathVars.append(":paren" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output += "\t"*self.blockLevel +  "(" + op + ", \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2)  + "),\n"
        if(appendAssign):
            self.output += "\t"*self.blockLevel +  "(assign, " +  str(args1) + ", \"" +  self.mathVars[-1] + "\"),\n"

    def op_mul_div_mod(self, args1, args2 = None, op = "store_mul"):
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
        if(self.isValidVariable(args2)):
            var2 = self.isValidVariable(args2)[0]
            self.output += "\t"*self.blockLevel +  "(" + op +", \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", \"" + str(var2)  + "\"),\n"
        else:
            self.output += "\t"*self.blockLevel +  "(" + op +", \"" +  self.mathVars[-1]  + "\", " +  str(args1)+ ", " + str(args2)  + "),\n"

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

    def op_sub(self, args1, args2 = None):
        self.op_add_sub(args1, args2, "store_sub")
    def op_add(self, args1, args2 = None):
        self.op_add_sub(args1, args2, "store_add")
    def op_div(self, args1, args2 = None):
        self.op_mul_div_mod(args1, args2, "store_div")
    def op_mul(self, args1, args2 = None):
        self.op_mul_div_mod(args1, args2, "store_mul")
    ################################################  MATH OPERATIONS END


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
            b = 0
            if(args2 == "true"): b = 1
            if(self.parentsLevel % 2 > 0):
                self.append_comment("\t"*self.blockLevel +  "# ---- boolean4: "+ self.mathVars[-2] +" and "+ self.mathVars[-3] +"\n")
                self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\", \"" + self.mathVars[-3]  +"\"),\n"
            else:
                if(len(self.mathVars) > 3):
                    self.append_comment("\t"*self.blockLevel +  "# ---- boolean4: "+ self.mathVars[-2] +" and "+ self.mathVars[-4] +"\n")
                    self.output += "\t"*(self.blockLevel) +  "(store_and,\""+ self.mathVars[-1]  +"\" ,\""+ self.mathVars[-2]  +"\", \"" + self.mathVars[-4]  +"\"),\n"
                else:
                    self.append_comment("\t"*self.blockLevel +  "# ---- boolean4: "+ self.mathVars[-2] +" and "+ self.mathVars[-3] +"\n")
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

    def op_neq_gt_lt_le_ge_eq(self, arg1, arg2, op = "neq"):        
        self.mathVars.append(":bgroup" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.append_comment("\t"*self.blockLevel +  "# ---- boolean: "+ str(arg1) +" "+ op + " "+ str(arg2) +"\n")
        self.output += "\t"*self.blockLevel +  "(assign, \""+ self.mathVars[-1]  +"\", 0),\n"
        self.output += "\t"*self.blockLevel +  "(try_begin),\n"
        self.output += "\t"*((self.blockLevel)+1) +  "("+ op +"," 
        if(isNumber(arg1)): self.output += str(arg1)
        else: 
            if(str(arg1[0] != '$')):
                self.output += "\":" + str(arg1) + "\""
        
        self.output += ","

        if(isNumber(arg2)): self.output += str(arg2)
        else: 
            if (arg2 == None):
                var  = self.mathVars[-1]
                self.output += "\"" + var  + "\""
            elif(str(arg2[0] != '$')):
                self.output += "\":" + str(arg2) + "\""
        self.output += "),\n"
        self.output += "\t"*((self.blockLevel)+1) +  "(assign, \""+ self.mathVars[-1]  +"\", 1),\n"
        self.output += "\t"*self.blockLevel +  "(try_end),\n"
        self.append_comment("\t"*self.blockLevel +  "# ---- end ---\n")


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
            if(self.enteredIf):
                self.output += "ENTERED IF 3"

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



    def op_neq(self, arg1, arg2):        
        self.op_neq_gt_lt_le_ge_eq(arg1, arg2, "neq")
    def op_gt(self, arg1, arg2):        
        self.op_neq_gt_lt_le_ge_eq(arg1, arg2, "gt")
    def op_ge(self, arg1, arg2):        
        self.op_neq_gt_lt_le_ge_eq(arg1, arg2, "ge")
    def op_le(self, arg1, arg2):        
        self.op_neq_gt_lt_le_ge_eq(arg1, arg2, "le")
    def op_lt(self, arg1, arg2):        
        self.op_neq_gt_lt_le_ge_eq(arg1, arg2, "lt")
    def op_eq(self, arg1, arg2):        
        self.op_neq_gt_lt_le_ge_eq(arg1, arg2, "eq")

    ################################################  BOOLEAN OPERATIONS END
    def return_expression(self, arg):
        if(isNumber(arg)):
            self.output += "\t"*self.blockLevel +  "(assign, reg"+ str(self.returnRegCounter) +", " + str(arg)  + "),\n"
        elif(isBooleanLiteral(str(arg.children[0]))):
            self.output += "\t"*self.blockLevel +  "(assign, reg"+ str(self.returnRegCounter) +", " + str(ConvertBooleanLiteralToNumeric(arg))  + "),\n"
        else:            
            var = self.isValidVariable(str(arg.children[0]))[0]
            self.output += "\t"*self.blockLevel +  "(assign, reg"+ str(self.returnRegCounter) +", \"" + str(var)  + "\"),\n"
        self.returnRegCounter += 1

    def result(self, *args):
        if(self.returnRegCounter != len(self.returnTypes)):
            raise Exception( "COMPILER ERROR: function results returned are " + str(self.returnRegCounter) + " Should be " + str(len(self.returnTypes)) + " results. "+ "At procedure/function " + self.currentProcedureName )
        self.returnRegCounter = 0 

    def expression(self, arg1=None):
        if(arg1 == None):
            arg1 = self.mathVars[-1]
        else:
            self.literals.append(arg1)
            #del self.mathVars[:]
            self.mathVars.pop()
        print("# expr " +  str(arg1))

    def multiple_assignment (self, *args):
        for arg in args:
            self.isValidVariable(arg)
            self.assignMultipleValueFromFunc.append(arg)
    
    def assignment(self, arg1, arg2=None, *args):
        
        vars = dict(self.vars)
        if(len(self.assignMultipleValueFromFunc) > 0):
            i = 0
            for var in self.assignMultipleValueFromFunc:
                self.output +=  "\t"*self.blockLevel  +  "(assign, \"" +  var + "\", \"" + self.mathVars[-1 * i] +"\"),\n" 
                i += 1 
            del self.assignMultipleValueFromFunc[:]
            return
        if(arg1 == None):
            arg1 = self.lastVariableNameDeclared[0]
        if(arg2==None):
            #print(vars[":" + arg1])
            if (arg1 == None):
                arg2 = DecorateWithQuotes(str(arg2))
                #self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + self.lastVariableNameDeclared[0]   + "\", " +  str(arg2) + "),\n"    
            elif(self.isValidVariable(arg1)):
                var = self.isValidVariable(arg1)
                self.output +=  "\t"*self.blockLevel  +  "(assign, \"" +  var[0] + "\", \"" + self.mathVars[-1] +"\"),\n" 
                self.lastAssignedVariable = var
                self.lastAssignedValue = self.mathVars[-1]
                del self.mathVars[:]
        else:            
            self.parentsLevel = 1
            variable = self.isValidVariable(arg1)
            variable2 = self.isValidVariable(arg2)
            arg1 = variable[0]
            if(variable2):
                arg2 = variable2[0]
            if(arg2 == None):
                if(len(self.mathVars) > 0 ):
                    self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1  + "\", " +  self.mathVars[-1] + "),\n"
                    var = self.isValidVariable(arg1)
                    self.lastAssignedVariable = var
                    self.lastAssignedValue = self.mathVars[-1]
                else:
                    self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1  + "\", " + str(0) + "),\n"
                    var = self.isValidVariable(arg1)
                    self.lastAssignedVariable = var
                    self.lastAssignedValue = str(0)
            elif(variable2):
                if(variable[1] == variable2[1]):
                    self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1  + "\", \"" +  arg2 + "\"),\n"
                    var = self.isValidVariable(arg1)
                    self.lastAssignedVariable = var
                    self.lastAssignedValue = arg2 
                else:
                    raise Exception( "COMPILER ERROR: " + arg1 + " is being assigned with incorrect data type. assigned value: " + str(arg2) + ", expected: " + variable[1] + ". At procedure/function " + self.currentProcedureName )                                
            elif(variable[1]=="Boolean"):
                if str(arg2) == "true":
                    self.append_comment("\t"*self.blockLevel+  "# "+ str(arg1) + " := true (1) " + "\n")
                    arg2 = 1
                elif str(arg2) == "false":
                    self.append_comment("\t"*self.blockLevel+  "# "+ str(arg1) + " := false (0) " + "\n")
                    arg2 = 0
                else: 
                    raise Exception( "COMPILER ERROR: " + arg1 + " is being assigned with incorrect data type. assigned value: " + str(arg2) + ", expected: boolean true or false" + ". At procedure/function " + self.currentProcedureName )                                
                self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1  + "\", " +  str(arg2) + "),\n"
                var = self.isValidVariable(arg1)
                self.lastAssignedVariable = var 
                self.lastAssignedValue = str(arg2)
            elif(variable[1]=="Number"):
                self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1  + "\", " +  str(arg2) + "),\n"
                var = self.isValidVariable(arg1)
                self.lastAssignedVariable = var 
                self.lastAssignedValue = str(arg2)
                if(not isNumber(arg2)):
                    raise Exception( "COMPILER ERROR: " + arg1 + " is being assigned with incorrect data type. assigned value: " + str(arg2) + ", expected: Numeric" + ". At procedure/function " + self.currentProcedureName )
            else:
                self.output +=  "\t"*self.blockLevel  +  "(assign, \"" + arg1  + "\", \":" +  str(arg2) + "\"),\n"
                var = self.isValidVariable(arg1)
                self.lastAssignedVariable = var 
                self.lastAssignedValue = str(arg2)


    def variabledeclare(self, arg1, arg2):
        if(arg1 in reservedKeywords):
            raise Exception("COMPILER ERROR: " + arg1 + " is reserved keyword! At procedure/function " + self.currentProcedureName )
        vars = dict(self.vars)
        if( ":" + arg1 in vars):
            raise Exception("COMPILER ERROR: " + arg1 + " is already defined!  At procedure/function " + self.currentProcedureName)
        
        for glob in self.globals:
            if(glob[0] == arg1):
                raise Exception("COMPILER ERROR: " + arg1 + " is already defined at " + glob[2] + " as " + glob[1] + ". At procedure/function " + self.currentProcedureName )
        
        if(str(arg1)[0] != "$"):
            self.append_comment("\t"*self.blockLevel+  "# var declare: "+ str(arg1) + " type :" + str(arg2)  + "\n")
            self.output +=  "\t"*self.blockLevel+ "(assign, \":" + str(arg1) + "\", 0),\n" 
            self.vars.append(( ":" + arg1, str(arg2)))
            self.lastVariableNameDeclared  = (":" + arg1, str(arg2))
        else:
            self.append_comment("\t"*self.blockLevel+  "# var declare global: "+ str(arg1) + " type :" + str(arg2)  + "\n")
            self.output +=  "\t"*self.blockLevel+ "(assign, \""+ str(arg1) + "\", 0),\n" 
            self.globals.append(( arg1, arg2, self.currentProcedureName))
            self.lastVariableNameDeclared  = (arg1, arg1)

    def variabledeclareparams(self, arg1, arg2):
        if(arg1 in reservedKeywords):
            raise Exception("COMPILER ERROR: " + arg1 + " is reserved keyword! At procedure/function " + self.currentProcedureName )
        self.append_comment("\t"*self.blockLevel+  "# var declare: "+ str(arg1) + " type :" + str(arg2)  + "\n" )
        self.vars.append(( ":" + str(arg1), str(arg2)))
        self.paramsdeclares.append((":" + str(arg1), str(arg2)))


    def block(self, *args):
        if(self.blockLevel == 1):
            print("# no tbe block")
        #self.blockLevel += 1
        #print "# block " + str(args)

    def test_expression(self, arg):
        if(arg == None and self.else_if_counter == 0):
            self.blockcondition = "(eq, \"" + self.mathVars[-1] + "\", 1), \n"
            self.enteredIf  = True
        elif(arg == None and self.else_if_counter > 0):
            if(len(self.loopEndIterators) > 0):
                self.blockcondition = "(eq, \"" + self.mathVars[-1] + "\", 1), \n"
            else:
                self.blockcondition = "(eq, \"" + self.mathVars[-1] + "\", 1), \n"
        else:
            if arg == "true":
                self.blockcondition = "(eq, 1,1), \n"
            elif arg == "false":
                self.blockcondition =  "(eq, 1,0), \n"
        del self.mathVars[:]

    def else_if_block(self, *args):
        pass
    
    def for_loop_end_cond(self, arg):
        self.enteredLoop = True
        if(arg == None):
            var = self.isValidVariable(self.mathVars[-1])
            if(var[1] == "Boolean"):
                raise Exception("cannot use boolean value here 1")
            self.output = self.output.replace("\xEE REPLACE \xEE", "\"" + self.mathVars[-1] + "\"") 
            self.loopEndIterators.append(self.mathVars[-1])
            self.output +=  "\t"*(self.blockLevel)+ "(gt, \""+  str(self.lastAssignedVariable[0]) + "\", \"" + self.mathVars[-1] + "\"),\n"
            self.append_comment("\t"*(self.blockLevel) + "# -- loop header end\n")
        else:
            var = self.isValidVariable(str(arg))
            if(var):
                if(var[1] != self.lastAssignedVariable[1]):
                    raise Exception("does not match")
                elif(var[1] == "Boolean"):
                    raise Exception("cannot use boolean value here 2")
                self.loopEndIterators.append(var[0])
                self.output = self.output.replace("\xEE REPLACE \xEE", "\"" + str(var[0]) + "\"" ) 
                self.output = self.output.replace("\n\t"*(self.blockLevel - 1)+"\xEE REPLACE2 \xEE", "\n" ) 
                self.output +=  "\t"*(self.blockLevel)+ "(gt, \""+  str(self.lastAssignedVariable[0]) + "\", \"" + str(var[0])  + "\"),\n"
                self.append_comment("\t"*(self.blockLevel) + "# -- loop header end\n")
            else:
                if(isBooleanLiteral(str(arg))):
                    raise Exception("cannot use boolean value here 3")
                self.mathVars.append(":paren" + str(self.parentsLevel))
                self.output = self.output.replace("\xEE REPLACE2 \xEE", "(assign, \"" + self.mathVars[-1] + "\", 99999999),\n") 
                self.parentsLevel += 1
                self.output +=  "\t"*(self.blockLevel)+ "(assign, \""+  self.mathVars[-1] + "\", "+ str(arg) + "),\n"
                self.output = self.output.replace("\xEE REPLACE \xEE", "\"" + self.mathVars[-1] + "\"")                 
                self.loopEndIterators.append(self.mathVars[-1])
                self.output +=  "\t"*(self.blockLevel)+ "(gt, \""+  str(self.lastAssignedVariable[0]) + "\", \"" + self.mathVars[-1] + "\"),\n"
                self.append_comment("\t"*(self.blockLevel) + "# -- loop header end\n")

    def for_loop_header(self, *args):
        self.blockLevel += 1
        if(isVariable(self.lastAssignedValue)):
            self.lastAssignedValue = "\"" + self.lastAssignedValue + "\"" 
        self.append_comment("\t"*(self.blockLevel - 1) + "# -- loop header begin\n")
        self.output +=  "\t"*(self.blockLevel - 1)+ "\xEE REPLACE2 \xEE"
        self.output +=  "\t"*(self.blockLevel-1)+ "(try_for_range, \""+  str(self.lastAssignedVariable[0]) + "\", "+ self.lastAssignedValue + ", \xEE REPLACE \xEE),\n"
        
    def while_header(self, *args):
        self.blockLevel += 1
        if(isVariable(self.lastAssignedValue)):
            self.lastAssignedValue = "\"" + self.lastAssignedValue + "\"" 
        self.mathVars.append(":while_loop" + str(self.parentsLevel))
        self.parentsLevel += 1
        self.output +=  "\t"*(self.blockLevel-1)+ "(try_for_range, \""+  str(self.mathVars[-1]) + "\", 0, \xEE REPLACE \xEE),\n"

        


    def beginblock(self, *args):
        if(self.enteredIf):
            self.else_if_counter += 1
        if( self.else_if_counter > 1):
            self.append_comment("\t"*(self.blockLevel) + "# -- here up to try_else was test expression \n")            
        else:
            self.append_comment("\t"*(self.blockLevel) + "# -- here up to try_begin was test expression \n")                        
            
        self.output += "\t"*(self.blockLevel) + self.blockcondition
        self.append_comment("\t"*(self.blockLevel) + "# -- if/else if header ends here \n")
        self.blockcondition = ""

    def if_try (self, *args):
        if(self.else_if_counter == 0):
            self.blockLevel += 1
            self.output +=  "\t"*(self.blockLevel-1)+ "(try_begin),\n"
            self.enteredIf = True

    def else_try(self, *args):  
        self.output +=  "\t"*(self.blockLevel-1)+ "(else_try),\n" 
        self.append_comment("\t"*(self.blockLevel) + "# -- else \n")
        print("else!")

    def endblock(self, *args):
        self.blockLevel -= 1
        self.output +=  "\t"*self.blockLevel+ "(try_end),\n" 
        self.else_if_counter = 0
        print("begin!")

    def endloopfor(self, *args):
        self.loopEndIterators.pop()
        self.blockLevel -= 1
        self.output +=  "\t"*self.blockLevel+ "(try_end),\n" 

    def returnsdeclare(self, *args):
        for ar in args:
            self.returnTypes.append(str(ar))        

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
        proc = self.WriteDocumentation()
        proc += "(\"" + self.currentProcedureName  + "\",[\n"
        proc += self.output 
        proc += "]),"
        procedures.append(proc)
        self.proceduresName[-1] = (self.currentProcedureName, self.paramsdeclares[:], [])
        self.reset()
        print("# procedure" + str(args))

    def function(self, *args):
        proc = self.WriteDocumentation()
        proc += "(\"" + self.currentProcedureName  + "\",[\n"
        proc += self.output 
        proc += "]),"
        self.proceduresName[-1] = (self.currentProcedureName, self.paramsdeclares[:] ,self.returnTypes[:])
        procedures.append(proc)
        self.reset()
        print("# function" + str(args))

    def reset(self):
        self.blockLevel  =1 # clear every procedure
        self.output = "" # clear every procedure
        del self.mathVars[:] # clear every procedure
        del self.paramsdeclares[:] # clear every procedure
        del self.vars[:] # clear every procedure
        del self.returnTypes[:] # clear every procedure
        del self.loopEndIterators[:]  # clear every procedure
        self.returnRegCounter = 0 # clear every procedure
        self.enteredIf = False # clear every procedure

    def procedure_name(self, arg1):
        self.currentProcedureName = str(arg1)
        for s in self.proceduresName:
            if(self.currentProcedureName == s[0]):
                raise Exception("COMPILER ERROR: redefinition of procedure/function " + self.currentProcedureName + " (it is already exist)")
        self.proceduresName.append((self.currentProcedureName, [] , []))

    def isValidVariable(self, var):
        var = str(var)
        if(isNumber(var)): return False
        if(isBooleanLiteral(var)): return False
        if(var[0] == "$"):
            for glob in self.globals:
                if var == glob[0]: return glob
            raise Exception( "COMPILER ERROR: undefined " + var + " for global variable. At procedure/function " + self.currentProcedureName)
        for v in self.vars:
            if(v[0] == ":" + var): return v
            if(v[0] == var): return v
        for v in self.mathVars:
            if("\"" + v + "\"" == var): return (v, self.InternalVariable(v))
            if( v == var): return (v, self.InternalVariable(v))
        for proc in self.proceduresName: 
            if(var == proc[0]):
                if(len(proc[2]) > 0):
                    return  ("script_" + var, "Function")
                else:
                    return  ("script_" + var, "Procedure")
        raise Exception( "COMPILER ERROR: undefined " + var + " for local variable. At procedure/function " + self.currentProcedureName)
        

    def WriteDocumentation(self):
        proc =  "\t #script_" +  self.currentProcedureName + "\n"
        proc += "\t #Input: \n" 
        for s in self.paramsdeclares:
            proc += "\t #  - "  + s[0] + " as "+ s[1]+ "\n" 
        proc += "\t #Output: \n"
        if(len(self.returnTypes) == 0):
            proc += "\t #  - None (procedure) \n"
        else:
           i = 0
           for s in self.returnTypes:
                proc += "\t #  - reg"  + str(i) + " as "+ s+ "\n"
                i += 1
        return proc

    def FindProcedureOrFunction(self, name):
        for n in self.proceduresName:
            if(n[0] == name):
                return n
        return None

    def InternalVariable(self, name):
        if(name.startswith(":bgroup")): return "Boolean"
        if(name.startswith(":paren")): return "Number"
        return False

    def append_comment(self, text):
        if(DEBUG):
            self.output += text

    def append_warning(self, text):
        self.output += "# WARNING: " + text + "\n"



turtle_grammar = """
start: (procedure | function)+ 

?procedure: "procedure" procedurename paramsdeclare  mainblock
?function: "function" procedurename paramsdeclare ":" returnsdeclare  mainblock

exitprocedure: "die"

?procedurename: NAME -> procedure_name

paramsdeclare : "("")"  
				| "(" NAME ":" TYPE ")" 
		        | "(" NAME ":" TYPE ("," NAME ":" TYPE)+ ")" 

returnsdeclare  : "("")"
                | "(" TYPE ")" 
		        | "("  TYPE (","  TYPE)+ ")" 


mainblock :     "begin" "end"  
                |"begin" NEWLINE*  "end"  
				| "begin" (instruction)* "end" 

beginblock: "then"
endblock: "end"
endloopfor:  "end"
endwhile: "end"
if_try : "if"
else_if_try: else_try if_try
else_try: "else"

test : "(" (expression | BOOL ) ")" -> test_expression


for_loop_header: assignment  
for_loop_end_cond: expression
loop_body:  (instruction)*

forstatement:  "for" for_loop_header "to" for_loop_end_cond "do" loop_body endloopfor 

while_header: "while" test "do" 
whilestatement: while_header loop_body endwhile

ifstatement: if_body endblock 
            | if_body (try_else_if_body)+ (try_else_body)? endblock  -> else_if_block


if_body: if_try  test beginblock (instruction)*
try_else_if_body : else_if_try test beginblock (instruction)* 
try_else_body: else_try (instruction)* 

     
?instruction: assignment ";"
            | variabledeclare ";"
            | exitprocedure ";"
            | result ";"
            | ifstatement
            | forstatement
            | whilestatement
            | procedure_expr ";" 

            

?expression :  bool_or
        ?bool_or: bool_and 
            | bool_or  "or" bool_and -> op_or

        ?bool_and: comp
            | bool_and  "and" comp -> op_and

        ?comp: sum
            | comp  ">=" sum -> op_ge 
            | comp  "==" sum -> op_eq 
            | comp  "<=" sum -> op_le 
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
             | "not" expression  -> op_neg             
             | function_expr 
             | NUMBER_NEG
             | BOOL
             | variable

    ?function_retmultple_expr: variable params -> op_func_call_mult_return
	?procedure_expr: variable params -> op_proc_call
    ?function_expr: variable params -> op_func_call
		?params:  "("")" 
			| "(" expression ")" 
			| "(" expression ("," expression)+ ")" 

return_expression: procedure_call_name | (NUMBER_NEG | NUMBER )

?result : ("result" return_expression) -> result
        | "result" return_expression ("," return_expression )+  -> result   

?assignment: variable "=" expression
           | variabledeclare "=" expression 
           | multiple_assignment "=" function_retmultple_expr

multiple_assignment : variable ("," variable)+ 


//           | variabledeclare "=" STRING 
//           | variable "=" STRING 




variabledeclareassign : NAME ":" TYPE ("=" expression) 
variabledeclare: NAME ":" TYPE 
indexing: variable "[" sum "]"  

?variable : NAME
procedure_call_name : variable

NAME: /\$?[A-Za-z][A-Za-z0-9_]*/
NUMBER: /\d+\.?\d*/
NUMBER_NEG: /\-\d+\.?\d*/
NEWLINE: /\\n|\\r/
STRING: /./
TYPE: "Number" | "String" | "QString" | "Procedure" | "Function" | "Boolean"
    | "Faction" | "Presentation" | "Troop" | "Agent" | "Item" | "Array" | "DynamicArray"
BOOL: "true"
	| "false"

COMMENT     : "/*" /(.|\\n|\\r)+/ "*/"  
             |  "//" /(.)+(\\n|\\r)/ 
 
%ignore COMMENT 
%import common.WS
%ignore WS
"""

parser = Lark(turtle_grammar, parser='lalr', transformer=CalculateTree(), debug=False)



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
            $GLOBAL2: Boolean;
            $GLOBAL: Number;
            if(2 < 1 + 3+ 4 + 5 * $GLOBAL and $GLOBAL2) then
                $GLOBAL = 1;
            else if (false) then
                $GLOBAL = 1;
            else
                $GLOBAL = -1;
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