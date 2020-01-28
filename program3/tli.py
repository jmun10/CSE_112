#! /usr/bin/env python3
import fileinput
import sys

# reading input: separate values for input with spaces.
# used to store a parsed TL expressions which are
# constant numbers, constant strings, variable names, and binary expressions
class Expr:
    def __init__(self, op1, operator, op2=None):
        self.op1 = op1
        self.operator = operator
        self.op2 = op2

    def __str__(self):
        if self.op2 is None:
            return self.operator + " " + self.op1
        else:
            return self.op1 + " " + self.operator + " " + self.op2

    # evaluate this expression given the environment of the symTable
    def eval(self, symTable):
        # TODO need to throw exceptions for missing var at program line
        # in case any ops are vars, try to get value from symTable

        if validFloat(self.op1) == False and self.operator != "STRING":
                op1val = symTable[self.op1]

        else:
            if self.operator != "STRING":
                op1val = float(self.op1)

        if self.op2 is not None and validFloat(self.op2) == False:
            op2val = symTable[self.op2]


        if self.op2 is not None:
            if self.op2 in symTable:
                op2val = symTable[self.op2]
            else:
                op2val = float(self.op2)

        if self.operator == "STRING":
            return self.op1
        if self.operator == "GETCONSTANT":
            return op1val
        if self.operator == "var":
            return op1val
        if self.operator == "+":
            return op1val + op2val
        if self.operator == "-":
            return op1val - op2val
        if self.operator == "*":
            return op1val - op2val
        if self.operator == "/":
            return op1val / op2val

        # boolean expressions should return 0 or 1
        if self.operator == ">":
            if op1val > op2val:
                return 1
            return 0

        if self.operator == "<":
            if op1val < op2val:
                return 1
            return 0

        if self.operator == ">=":
            if op1val >= op2val:
                return 1
            return 0

        if self.operator == "<=":
            if op1val <= op2val:
                return 1
            return 0

        if self.operator == "==":
            if op1val == op2val:
                return 1
            return 0

        if self.operator == "!=":
            if op1val != op2val:
                return 1
            return 0
        else:
            #return 0
            raise Exception("Unrecognized operator for expression.")


# used to store a parsed TL statement
class Stmt:

    # only time exprs will be a multiple valued array is for print statements

    def __init__(self, keyword, exprs, varToAssign = None):
        self.keyword = keyword
        self.exprs = exprs
        self.varToAssign = varToAssign


    def __str__(self):
        others = ""
        for exp in self.exprs:
            others = others + " " + str(exp)

        optVar = ''
        if self.varToAssign is not None:
            optVar += ' ' + str(self.varToAssign) + ' ='

        return self.keyword + optVar + others

    # perform/execute this statement given the environment of the symTable
    def perform(self, symTable):
        #print("Doing: " + str(self))

        if self.keyword == "let":
            var = self.varToAssign

            symTable[var] = self.exprs[0].eval(symTable)
            return

        if self.keyword == "if":
            # varToAssign is the label to jump to
            label = self.varToAssign
            condition = self.exprs[0].eval(symTable)
            if condition:
                return label
            else:
                return


        if self.keyword == "input":                   # for input types, expr array is empty
            var = self.varToAssign
            takeInput = input()
            try:
                takeInput = float(takeInput)
            except:
                print("Illegal or missing input")
                quit()
            symTable[var] = takeInput
            return

        if self.keyword == "print":
            for i in range(len(self.exprs)):
                if i != 0:
                    print(" ",end="")
                print(self.exprs[i].eval(symTable), end="")

            print()


def createStmt(tokens):
     # takes a list of tokens, creates values accordingly
     # this function should be called at each prgm line to create statements

    if tokens[0] == "input":
        varToAssign = tokens[1]
        return Stmt("input", [], varToAssign)

    if tokens[0] == "let":         # add exception if
        varToAssign = tokens[1]
        expr = exprBuilder(tokens[3:])
        if tokens[2] != "=":
            raise Exception()
        return Stmt('let', [expr], varToAssign)

    if tokens[0] == "if":
        #goto should be tokens[2] or tokens[4]
        # TODO currently building

        if tokens[2] == "goto":
            jumpto = tokens[3]
            expr = exprBuilder(tokens[1])
            return Stmt("if", [expr],jumpto)
        if tokens[4] == "goto":
            jumpto = tokens[5]
            expr = exprBuilder(tokens[1:4])
            return Stmt("if", [expr],jumpto)

        raise Exception()

    else:
        raise Exception()

    return


# given a list of tokens, parses and returns the correct expression
def exprBuilder(tokens):
    validOperators = ["+","-","*","/","<",">","<=",">=","==","!="]
    # if only 1 token, can be a constant or variable name
    # only other option is 3 tokens, can be a binary expression
    if len(tokens) == 1:
        #check if expression should be just a constant
        if validFloat(tokens[0]):
            return Expr(tokens[0],"GETCONSTANT")
        else:
            return Expr(tokens[0], "var")

    if len(tokens) == 3 and tokens[1] in validOperators:
        return Expr(tokens[0], tokens[1], tokens[2])

    raise Exception()

    return


#checks if a string is also a valid float
def validFloat(string):
    #check number of decimal places, remove decimal if present, then try to convert to int
    if string.count(".") > 1:
        return False

    s1 = string.replace(".","")
    if s1.isdigit():
        return True
    return False


def parseFile():
    args = len(sys.argv)
    if args != 2:
        print("tli.py only takes one argument")
        quit()

    # reads file input and strips newline from text

    text_file = open(sys.argv[1], "r")
    lines = text_file.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()

    # creates tokens from lines
    for i in range(len(lines)):
        lines[i] = lines[i].split()

    return lines


def parseLines(lines,labelTable):
    allStmts = []

    for i in range(len(lines)):
        firstToken = lines[i][0]

        if hasLabel(firstToken):

            label = firstToken[0:len(firstToken)-1]
            labelTable[label] = i+1

            #strips label from line after appending to labelTable
            lines[i] = lines[i][1:len(lines[i])]

        #custom split for print stmts
        if lines[i][0] == "print":
            exprs = []
            quotes = ["\"", "\'"]
            remExpr = lines[i][1:]
            remExpr = "".join(remExpr)
            remExpr  = remExpr.split(",")
            #print(remExpr)

            for i in range(len(remExpr)):
                if remExpr[i][0] in quotes and remExpr[i][len(remExpr[i]) - 1] in quotes:
                    exprs.append(Expr(remExpr[i][1:len(remExpr[i])-1],"STRING"))
                else:
                    exprs.append(exprBuilder(remExpr[i].split()))

            allStmts.append(Stmt("print",exprs))

        else:
            try:
                allStmts.append(createStmt(lines[i]))
            except:
                print("Syntax Error on line " + str(i+1))
                quit()

    return allStmts


def hasLabel(token):
    if token[len(token)-1] == ":":
        return True
    return False


def main():

    # Symbol Table     [ var : value ]     ->   [ str : int ]
    symTable = {}
    # labels to lines    [ label : line ]   ->   [ str : int ]
    labelTable = {}
    lines = parseFile()
    statements = parseLines(lines,labelTable)

    pc = 1

    while pc <= len(lines):
        #print("executing line " + str(pc))
        curstmt = statements[pc-1]

        # handles jumping around labels
        if curstmt.keyword == "if":
            condition = curstmt.perform(symTable)
            if condition:
                try:
                    pc = labelTable[curstmt.varToAssign]
                    continue
                except:
                    print("illegal goto " + curstmt.varToAssign + " at line " + str(pc))
                    quit()


        #for everything else
        statements[pc-1].perform(symTable)
        pc+=1


main()