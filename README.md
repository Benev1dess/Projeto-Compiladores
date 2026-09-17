# Analisador Léxico - Linguagem TONTO

Este projeto implementa um Analisador Léxico para a linguagem TONTO, construído em Python, utilizando a biblioteca PLY. O sistema lê um arquivo e emite um relatório sobre o código do arquivo.

## Funcionalidades
* Mapeia mais de 40 palavras reservadas.
* Identificadores incorretos geram erro e retornam mensagens indicando exatamente qual regra foi violada (ex: uso indevido de números ou sublinhados).
* Calcula e exibe a linha e a coluna de cada token ou erro encontrado no texto fonte.
* No fim da execução, gera um relatório contabilizando as ocorrências de cada categoria léxica (Classes, Relações, Instâncias, etc.).

## Como Executar
Para rodar o analisador na sua máquina, certifique-se de ter o Python 3 instalado e siga os passos abaixo:

1. Instale a dependência do PLY:
    ```bash
    pip install ply
    ```

2. Execute o script no terminal:
    Digite o comando abaixo no terminal do VS Code, substituindo pelo caminho do seu arquivo.
    ```bash
    python lexer.py nome_do_arquivo.tonto
    ```

## Regras de Nomenclatura (Tokens Customizados)
O analisador usa regras baseadas em expressões regulares e validação para triar os identificadores criados pelo usuário:

* **Classes (`CLASS_NAME`)**: Devem iniciar com letra maiúscula e não podem conter números.
* **Relações (`RELATION_NAME`)**: Devem iniciar com letra minúscula e não podem conter números.
* **Instâncias (`INSTANCE_NAME`)**: Devem iniciar com letra e, obrigatoriamente, terminar com um número.
* **Tipos Customizados (`CUSTOM_DATATYPE`)**: Devem terminar exatamente com o sufixo `DataType`, iniciar com letra, e não possuir números ou sublinhados.
* **Bloqueio Global**: Nenhum identificador pode começar com sublinhado (`_`).
