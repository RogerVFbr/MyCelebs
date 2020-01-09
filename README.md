# ev-desafio


Desafio técnico para a empresa E.V. Requisitos atendidos:

### Relativo às observações
* O projeto está todo contido na branch master.
* Link deste repositório: https://github.com/RogerVFbr/ev-contacts
* Link para o deploy: https://ev-desafio.firebaseapp.com
* Arquivos com informações sensíveis foram omitidos do commit (chaves de api).

### Etapa 1
* O CRUD foi todo feito diretamente no Firebase.
* O LocalStorage foi utilizado para implementar um sistema de log local.
* Foi implementado um fluxo de registro de contatos utilizando o ViaCep conforme indicado.

### Etapa 2
* Estão implementados a medida de distância em linha reta, o clima no endereço e o link que abre a rota.

### Etapa 3
* CSS do app foi customizado.
* URL Endpoint para expor os contatos do banco: https://ev-desafio.firebaseio.com/contacts.json
* Firebase auth implementado para modificações e banco de dados bloqueado para operações de escrita sem autenticação.

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
