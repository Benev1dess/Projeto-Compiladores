# Analisador Sintático — Linguagem TONTO

Este projeto implementa um analisador sintático para a linguagem TONTO, desenvolvido em Python 3 com a biblioteca PLY.

O programa lê arquivos com extensão `.tonto`, utiliza o analisador léxico para identificar os tokens e verifica se as declarações seguem as regras gramaticais definidas.

## Funcionalidades

O analisador sintático reconhece:

- Declarações de pacotes (`package`) e importações (`import`).
- Declarações de classes e seus estereótipos, como `kind`, `role`, `phase` e `subkind`.
- Especializações entre classes (`specializes`).
- Atributos, tipos de dados e metadados.
- Enumerações (`enum`) e tipos personalizados (`datatype`).
- Conjuntos de generalização (`genset`).
- Relações internas e externas e suas cardinalidades.
- Erros sintáticos, informando a linha, a coluna e o token inesperado.

## Requisitos

- Python 3 instalado.
- Biblioteca PLY.

## Instalação

Abra o terminal na pasta do projeto e instale a dependência:

```bash
python3 -m pip install ply
```

## Como executar

Na pasta do projeto, execute:

```bash
python3 parser.py arquivo.tonto
```

Substitua `arquivo.tonto` pelo nome do arquivo que deseja analisar.

Por exemplo:

```bash
python3 parser.py Pessoa.tonto
```

Também é possível executar a análise em outros arquivos:

```bash
python3 parser.py UBS.tonto
python3 parser.py Vacinacao.tonto
python3 parser.py ConsultaMedica.tonto
```

Os arquivos `parser.py`, `lexer.py` e o arquivo `.tonto` informado devem estar em locais acessíveis pelo comando executado.

## Exemplo de código TONTO

```text
import Hospital

package Clinica

kind Pessoa

role Paciente specializes Pessoa
```

Nesse exemplo, o programa identifica uma importação, o pacote `Clinica` e duas declarações de classes, sendo uma delas uma especialização de `Pessoa`.

## Resultado da análise

Após a execução, o programa apresenta no terminal o nome do pacote, as importações, a quantidade de declarações e as informações reconhecidas.

Caso encontre um erro sintático, apresenta uma mensagem com sua localização e interrompe a análise.

## Estrutura principal

- `lexer.py`: realiza a análise léxica, identificando e fornecendo os tokens.
- `parser.py`: realiza a análise sintática, verificando as regras gramaticais e apresentando os resultados.
- Arquivos `.tonto`: contêm os códigos utilizados como entrada para a análise.

## Funcionamento

O programa lê o conteúdo do arquivo informado e cria uma instância do analisador léxico. Durante a execução, o parser recebe os tokens do lexer e verifica se eles correspondem às produções gramaticais.

Quando a análise é concluída, as informações reconhecidas são organizadas e apresentadas no terminal. O analisador verifica a estrutura sintática do código, não a validade semântica das declarações.