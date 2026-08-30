# DOCUMENTATION and Use Case for RadioSkySimsSuite

**TODO**

- garantir linting limpo
- avaliar o documento que segue e verificar todas as novas features que são necessárias.
- construir um plano de implantação destas features
- Complementar o plano de documentação exposto, garantindo umaq boa cobertura de funcionalidades e exemplos de uso.
- Limpar documentação, notebooks e raiz, mantendo apenas informações apropriadas para o estagio de desenvolvimento atual. Remover documentos históricos da arvore e refazer análise dertalhada da qualidade de código.
- NEW FEATURE: exportal cli para gerar TODs a partir de um arquivo de configuração, com visualização de progresso e com a opção de rodar em background
- NEW_FEATURE: permitir rodar simulações non-blocking em notebooks, com visualização de progresso e com a opção de rodar em background ou retornar para foreground ou terminar.
- Avaliar devolutiva dos planos antes de prosseguir.

## Formato 

- Este documento fornece subsídios para a criação de uma documentação.
- A documentação científica será toda feita em inglês, usando mystmd, com contexto físico e explicações das operações.
- O documento mostrará blocos de código em python presentes em notebooks associados, com o output das células cacheados.
- Notebooks que usem print de maneira minimalista, dando preferencia aos output dos loggers
- Sem utilização de emojis


## Project Description

- texto de um ou dois parágrafos sobre o projeto, com o objetivo de ser uma introdução para a documentação científica.

## Project Structure

- Módulos disponíveis com descrição de suas funcionalidades em tabela
- filetree do projeto

## Installlation

- database schema initialization
- satellite_update

## DataBase and Persistence

## Creating the Database

## Configuration

## Software Archtecture

## Radiotelescope

- Use frequency_range and time_range
Instantiate a radiotelescope from inline parameters
- Instantiate a radiotelescope from settings
- Plot OSM map of radiotelescope location (built in)
- View antenna beam response and properties (built in)
- view pointing properties Alt Az, Ra Dec
- view skychart mollweide icrs for pointings in time_range with beam fwhm


## Satellites

### From TLE

- load signals info from custom signals.json
- Create Satellites from a COnstellation
- Create tracks from a time_range
- view tracks on a skychart mollweide icrs (built in method in tracks)
- view tracks projected on earth (built in method in tracks, individually or with kde heatmap)
- signal properties (Power, EIRP, frequency, modulation)
- view PSD


### from RINEX

- Create Satellites from a COnstellation
- Create tracks from a time_range
- view tracks on a skychart mollweide icrs (built in method in tracks)
- view tracks projected on earth (built in method in tracks, individually or with kde heatmap)
- signal properties (Power, EIRP, frequency, modulation)
- view PSD
- option to export power information to signals.json

## LocalSources

### Sun

### Custom Made LocalSources

## RadioSources

### NVSS Sources

### TAP Query

### Using other catalogs

## Healpix Maps

## Simulations

### TOD

- Criar simulação com satelites, Sun e NVSS

### Maps

## Waterfall Visualization

## Physical Units and Conventions

## Performance

## File Formats

## Structure of the Project

### Technology Stack

### Project Structure

### Configurations (detailed view)

### Credentials

### Lazy Loading and Lazy Calculations

### Diagram of modules (Oerview)

### Class Diagram

### Sequence Diagram for Use Cases

### Database Schema

### Tests

## API docs