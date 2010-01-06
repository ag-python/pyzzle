

def select(input, value=None, key=None, duplicate=False,
           where=None, orderby=None, descend=False, 
           groupby=None, having=None):
    """Performs a linq style select query on an iterable. 
    All optional parameters must be functions, with the exception of descend. 
    Returns a dictionary if key is specified. Returns a list, otherwise"""
    if key: output={}
    else:   output=[]
    if not input: return output
    
    if groupby:
        groups={}
        for row in input:
            if not having or having(row):
                groups[groupby(row)]=row
        input=groups.keys()
    
    for row in input:
        if not where or where(row):
            if value:       item=value(row)
            else:           item=row
            
            if key:
                if not duplicate:
                    output[key(row)]=item
                elif key(row)in output:
                    output[key(row)].append(item)
                else:
                    output[key(row)]=[item]
            else:           
                output.append(item)
            
    if orderby and not key:
        output.sort(key=orderby, reverse=descend)
        
    return output

