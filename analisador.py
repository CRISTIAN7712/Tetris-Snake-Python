import re #Libreria para trabajar con expresiones regulares
import os #Libreria para trabajar con archivos y el SO
import json #Para trabajar en formato JSON

class Tokenizer: #Analizador léxico, donde se guarda el código y se almacenan los tokens
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []

    def tokenize(self):
        lines = self.source.splitlines() #Divide el código en lineas, elimina espacios blancos
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):  
                continue


            line = line.split("#", 1)[0].strip()  
            regex_tokens = re.findall(
                r'"([^"]*)"|'   #Captura elementos entre comillas             
                r'(\d+\.?\d*)|'     #Captura números o decimales
                r'({|}|\[|\]|=|,|:)|'     #Captura los símbolos especiales   
                r'([A-Za-zÁÉÍÓÚáéíóúñÑ_][\wÁÉÍÓÚáéíóúñÑ_]*)',  #Captura los identificadores
                line
            )
            # Analizamos los grupos capturados y los convertimos en tokens
            for group in regex_tokens:
                if group[0]:  
                    self.tokens.append(('STRING', group[0]))
                elif group[1]:  
                    if '.' in group[1]:
                        self.tokens.append(('NUMBER', float(group[1])))
                    else:
                        self.tokens.append(('NUMBER', int(group[1])))
                elif group[2]:  #
                    self.tokens.append(('OPERATOR', group[2]))
                elif group[3]:  
                    self.tokens.append(('IDENTIFIER', group[3]))

        return self.tokens


def load_file_content(filepath): #Lee el contenido de un archivo y lo retorna como texto
    if not os.path.exists(filepath):
        print(f"Error: El archivo '{filepath}' no existe.")
        return None

    with open(filepath, 'r', encoding='utf-8') as file: # Abrimos el archivo en modo lectura con codificación UTF-8
        return file.read()


def analizar_archivo(filepath, titulo): #Tokeniza y muestra los tokens de un archivo
    source_code = load_file_content(filepath)
    if source_code:
        print(f"\n===== {titulo.upper()} =====")
        tokenizer = Tokenizer(source_code)
        tokens = tokenizer.tokenize()
        for token in tokens:
            print(token)
            
# Probamos con los archivos Snake y Tetris
analizar_archivo("Snake.txt", "Snake")
analizar_archivo("Tetris.txt", "Tetris")




class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    #   Devuelve el token actual o EOF si ya no hay más
    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None)
    # Avanza al siguiente token verificando tipo y valor esperado
    def eat(self, expected_type=None, expected_value=None):
        tok_type, tok_val = self.current_token()
        if expected_type and tok_type != expected_type:
            raise SyntaxError(f"Se esperaba {expected_type}, pero se encontró {tok_type}")
        if expected_value and tok_val != expected_value:
            raise SyntaxError(f"Se esperaba {expected_value}, pero se encontró {tok_val}")
        self.pos += 1
        return tok_val
    # Inicia el análisis y construye un diccionario de configuraciones
    def parse(self):
        config = {}
        while self.current_token()[0] != 'EOF':
            key, value = self.parse_assignment()
            config[key] = value
        return config
    # Analiza asignaciones del tipo: clave = valor
    def parse_assignment(self):
        key = self.eat('IDENTIFIER')
        self.eat('OPERATOR', '=')
        value = self.parse_value()
        return key, value
    # Analiza el valor de una asignación
    def parse_value(self):
        tok_type, tok_val = self.current_token()

        if tok_type in ('STRING', 'NUMBER', 'IDENTIFIER'):
            self.eat()
            return tok_val
        elif tok_type == 'OPERATOR' and tok_val == '{':
            return self.parse_dict()
        elif tok_type == 'OPERATOR' and tok_val == '[':
            return self.parse_list()
        else:
            raise SyntaxError(f"Valor inesperado: {tok_type}, {tok_val}")
    # Analiza diccionarios { clave = valor }
    def parse_dict(self):
        self.eat('OPERATOR', '{')
        d = {}
        while not (self.current_token()[0] == 'OPERATOR' and self.current_token()[1] == '}'):
            key = self.eat('IDENTIFIER')
            self.eat('OPERATOR', '=')
            value = self.parse_value()
            d[key] = value
        self.eat('OPERATOR', '}')
        return d
    # Analiza listas [valor1, valor2, ...]
    def parse_list(self):
        self.eat('OPERATOR', '[')
        lst = []
        while not (self.current_token()[0] == 'OPERATOR' and self.current_token()[1] == ']'):
            lst.append(self.parse_value())
            if self.current_token()[0] == 'OPERATOR' and self.current_token()[1] == ',':
                self.eat('OPERATOR', ',')
        self.eat('OPERATOR', ']')
        return lst
    # Guarda la configuración en un archivo JSON
    def guardar_configuracion(self, config, filename):
        ruta_archivo = "./" + filename
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"Configuración guardada en {ruta_archivo}")
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")

source_code_snake = load_file_content("Snake.txt")
tokens_snake = Tokenizer(source_code_snake).tokenize()
tokens_snake.append(('EOF', None))
parser_snake = Parser(tokens_snake)
config_snake = parser_snake.parse()
config_snake_filename = "config_snake.ast"
parser_snake.guardar_configuracion(config_snake, config_snake_filename)

print("\n=== CONFIGURACIÓN SNAKE ===")
print(json.dumps(config_snake, indent=4, ensure_ascii=False))


source_code_tetris = load_file_content("Tetris.txt")
tokens_tetris = Tokenizer(source_code_tetris).tokenize()
tokens_tetris.append(('EOF', None))
parser_tetris = Parser(tokens_tetris)
config_tetris = parser_tetris.parse()
config_tetris_filename = "config_tetris.ast"
parser_tetris.guardar_configuracion(config_tetris, config_tetris_filename)

print("\n=== CONFIGURACIÓN TETRIS ===")
print(json.dumps(config_tetris, indent=4, ensure_ascii=False))