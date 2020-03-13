> Engenharia de Telecomunicações - Sistemas Distribuídos (STD29006)
>
> Instituto Federal de Santa Catarina - campus São José
>
> Osvaldo da Silva Neto



# Relatório


## Introdução



Os web services RESTful (Representational State Transfer) são adequados na utilização de cenários básicos e também melhor adaptados ao uso do protocolo HTTP comparando ao serviço SOAP. Os serviços RESTful são mais leves, o que significa que podem ser desenvolvidos com menor esforço, tornando-os mais fáceis de serem adotados como parte da implementação de um sistema.



## Web Service


O desenvolvimento de um web service RESTful é apropriado se por ventura não existir a necessidade de manter informações de estado e como não há uma descrição formal do funcionamento do serviço, tanto a aplicação que corresponde ao servidor do serviço quanto a que corresponde ao cliente ou o consumidor precisam entender e concordar com o contexto na troca de informações.[1]

Nos serviços RESTful, tanto os dados quanto as funcionalidades são considerados recursos e ficam acessíveis aos clientes através da utilização de URIs (Uniform Resource Identifiers), que normalmente são endereços na web e identificam tanto o servidor no qual a aplicação está hospedada quanto a própria aplicação e qual dos recursos oferecidos pela mesma está sendo solicitado.[1]


## Funcionalidade do Sistema

Com o objetivo de desenvolver uma aplicação Web Service Restfull, vimos neste projeto a possibilidade de explorar os conceitos básicos deste serviço.
Nossa aplicação conta com um sistema de compartilhamento de dados entre os sistemas operantes. Toda a comunicação entre processos será feita utilizando o serviço de Web Service, buscando explorar seus benefícios.
Para fins de simulação, nossa aplicação deve funcionar com a mesma configuração ilustrada abaixo:

![](/Draw/conexao.png)

Com nossa aplicação sendo centralizada em apenas um coordenador e podendo este se comunicar com outras duas replicas, onde toda operação a ser executada depende da autorização das mesmas.

Para colocar nossa aplicação em operação primeiramente devemos rodar as três aplicações (coordenador e duas réplicas) vale lembrar que o algoritmo é o mesmo para ambos os casos, portanto se desejar rodar as aplicações em uma única máquina será necessário informar portas diferentes passadas por argumentos em todas as aplicações, caso contrário não é necessário informar portas diferentes, porém ainda existe a necessidade de enviar a porta pela linha de comando. Segue abaixo exemplo de compilação python.

>> python main1.py "numero da porta escolhida"


Tendo todas as aplicações no modo de aguardo, agora podemos dar início as operações de nosso sistema. Primeiramente temos que enviar uma informação básica para nossas máquinas, que é responsável pela geração do sorteio simulação da operação, está operação é realizada enviando um "POST" enviado para a URL "http://0.0.0.0:'porta'/seed' para todas as nossas unidades com o dado a ser utilizado obedecendo o seguinte formato, caso seja feita este passo com sucesso nosso sistema irá retornar um código "201 created" com a semente enviada.

    { "seed" : "123456" }
    
Agora devemos eleger um coordenador para a operação, pois obedecendo as regras de negócio, apenas o coordenador pode enviar mensagens as réplicas, esta ação pode ser feita enviando um "POST" com uma lista no formato json para qualquer uma das aplicações ativas para a URL "http://0.0.0.0:'porta'/replica", segue abaixo formato da mensagem a enviar.

	{
		"replicas" : [
			{
				"id" : "replica 1",
				"endpoint" : "http://0.0.0.0:5001"
			},
			{
				"id" : "replica 2",
				"endpoint" : "http://0.0.0.0:5002"
			}
		]
	}

Onde nos campos de "id" deve nos informar a identidade da réplica e no "endpoint" deve nos informar o caminho das replicas. Esta mensagem deve ser enviada somente para o coordenador escolhido, case seja enviada com sucesso nesta fase será retornado um código "201 created", com uma lista das replicas.

Com nosso coordenador escolhido, podemos dar sequência ao processo enviando um "POST" para a URL "http://0.0.0.0:'porta/acoes" com os dados necessários para iniciação da operação. Segue abaixo formato da mensagem a enviar.

    {
        "id" : "19148f6d-1318-4887-b2b6-215bfc8ac35f",
        "operacao" : "debito",
        "conta" : "1234",
        "valor" : "10,00"
    }

Onde nos campos "id" deve conter uma identificação única para cada ação, no campo "operação" deve conter o tipo de operação (crédito ou débito), no campo "conta" deve nos informar a conta a executar a operação e por último o valor da operação no campo "valor". Vale resaltar que esta mensagem deve ser enviada somente para o processo coordenador, caso contrário será perdida a sincronia das listas armazenadas.

Enviando esta mensagem ao coordenador nosso sistema irá nos retornar com o código "201 created", caso seja concluída com sucesso ou "403 forbidden" caso não seja realizada, porém todas as operações enviadas ao coordenador acabam ficando registradas em uma memória interna do sistema no seguinte formato:

    { 
        "acoes" : [
            {
                "id" : "19148f6d-1318-4887-b2b6-215bfc8ac35f",
                "status" : "success"
            }
            {
                "id" : "0fcf8b5f-622b-4923-81c4-43b1753e403f",
                "status" : "fail"
            }
        ] 
    }

Esta lista pode ser capturada enviando um "GET" para a URL "http://0.0.0.0:'porta'/acoes" em qualquer uma das nossas máquinas, vale lembrar que todas devem conter a mesma lista.

Algumas outras operações que podem ser realizadas em nosso sistema:

"GET" para a URL "http://0.0.0.0:'porta'/contas" : nos retorna uma lista com todas as contas e saldos no seguinte formato.

    {
        "contas" : [
            {
                "numero" : "1234",
                "saldo" : "100,00"
            },
            {
                "numero" : "4345",
                "saldo" : "50,00"
            }
        ]
    }
    
"GET" para a URL "http://0.0.0.0:'porta'/replicas : nos retorna uma lista das réplicas existentes em nosso sistema, vale lembrar que o único que contém esta lista é o coordenador do sistema, se caso invocar este método nas replicas o sistema retornará um código "404 not found". Segue modelo de lista retornada pelo método.
	
	{
		"replicas" : [
			{
				"id" : "replica 1",
				"endpoint" : "http://0.0.0.0:5001"
			},
			{
				"id" : "replica 2",
				"endpoint" : "http://0.0.0.0:5005"
			}
		]
	}

"DELETE" para URL "http://0.0.0.0:'porta'/replicas" : se caso seja o coordenador retornará um código "200 ok" para informar a remoção com sucesso, caso contrário retornará "404 not found".

"POST" para a URL "http://0.0.0.0:'porta'/contas" : neste caso será reiniciado as contas, ou seja, todas os registros feitos anteriormente serão descartados, retornará um código "201 created" para informar a renovação da lista de contas, caso contrário retornará "400 abort". Este método deve ser enviado a todos as aplicações, tanto para o coordenador quanto para a réplica, para manter a sincronia do sistema.


## Considerações Finais

Ao concluir este projeto, podemos afirmar que trabalhar com Web Service não é uma tarefa difícil, porém sua execução necessita de um conhecimento dos termos exigidos pelo serviço.
Uma das principais vantagens do uso de web service é ter a capacidade de tratar tudo como recursos e ter uma forma segura e prática no acesso destes.


## Referências

[1] - https://www.devmedia.com.br/introducao-a-web-services-restful/37387

[2] - https://pt.wikipedia.org/wiki/REST

[3] - https://blog.caelum.com.br/rest-principios-e-boas-praticas/
