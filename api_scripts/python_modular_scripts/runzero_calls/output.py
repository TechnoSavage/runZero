import json
import pandas as pd

def output_format(format, filename, data):
    '''
        Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param filename: A String, the filename, minus extension.
        :para data: json data, file contents
        :returns None: Calls another function to write the file or prints the output.
    '''
    
    if format == 'json':
        filename = f'{filename}.json'
        write_file(filename, json.dumps(data))
    elif format == 'txt':
        filename = f'{filename}.txt'
        string_list = []
        for line in data:
            string_list.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        text_file = '\n'.join(string_list)
        write_file(filename, text_file)
    elif format in ('csv', 'excel', 'html'):
        write_df(format, filename, data)  
    else:
        for line in data:
            print(json.dumps(line, indent=4))
    
def write_df(format, filename, data):
    '''
        Write contents to output file. 
    
        :param format: a string, excel, csv, or html
        :param filename: a string, the filename, excluding extension.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
    df = pd.DataFrame(data)
    try:
        if format == "excel":
            df.to_excel(f'{filename}.xlsx', freeze_panes=(1,0), na_rep='NA')
        elif format == 'csv':
            df.to_csv(f'{filename}.csv', na_rep='NA')
        else:
            df.to_html(f'{filename}.html', render_links=True, na_rep='NA')
    except IOError as error:
        raise error
    
def write_file(filename, contents):
    '''
        Write contents to output file. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''

    try:
        with open( filename, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error