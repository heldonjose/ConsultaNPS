from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models import Sum, Count

from util import choicesModels
from util.choicesModels import CRIADA, FINALIZADA
from django.core.validators import MaxValueValidator, MinValueValidator

'''
Classe abstrata criada  para ter dados de data de criação do registro e ultima modificação do mesmo.
'''


class TimestampableMixin(models.Model):
    data_cadastro = models.DateTimeField(auto_now_add=True)
    date_modificado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


'''
Classe usuário tem uma relação One To One com o User do Django, 
para utilizar de todas as propriedades de autentiação
do framework.
O usuário tem o tipo.
   - PESQUISADOR
   - PESQUISADO
   
Obs:. Poderia ter usado somente o usuário do django e ter criado o grupo de acesso.
Fiz dessa maneira por que tenho mais prática, não gosto de usar o user do django para informações extra de
Usuário do meu sistema
'''


class Usuario(TimestampableMixin):
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ('nome',)

    user = models.OneToOneField(User,
                                on_delete=models.PROTECT,
                                related_name='usuario')
    nome = models.CharField(max_length=255, help_text='Nome do Usuário')
    email = models.CharField(max_length=255, help_text='Email, também usulizado como login')
    senha = models.CharField(max_length=100, help_text='Senha do Usuário')
    tipo = models.CharField('TIPO',
                            max_length=50,
                            choices=choicesModels.TIPO_USUARIO, )

    # Método para utilizar quando quiser retornar infomações do usuário sem precisar criar um Serializable
    def get_json(self):
        return dict(
            id=self.pk,
            nome=self.nome,
            login=self.email,
            token=self.user.auth_token.key,
            tipo=self.tipo,
        )


'''
Classe Pesquisa - Tem o título (descrição) e um status da pesquisa (CRIADA - INICIADA - FINALIZADA)
'''


class Pesquisa(TimestampableMixin):
    class Meta:
        verbose_name = 'Pesquisa'
        verbose_name_plural = 'Pesquisas'
        ordering = ('descricao',)

    descricao = models.CharField(u'Descrição', max_length=255, )
    status = models.CharField('TIPO',
                              max_length=50,
                              default=CRIADA,
                              choices=choicesModels.STATUS_PESQUISA)

    def __str__(self):
        return self.descricao

    # Método para utilizar quando quiser retornar infomações do básicas da pesquisa
    def get_json(self):
        questoes = [questao.get_json() for questao in self.questoes_pesquisas.all()]
        return dict(
            id=self.pk,
            descricao=self.descricao,
            status=self.status,
            questoes=questoes,
        )

    # Método para utilizar quando quiser retornar infomações do detalhadas da pesquisa
    def get_json_detalheNPS(self):
        questoes = [questao.get_json() for questao in self.questoes_pesquisas.all()]
        return dict(
            id=self.pk,
            descricao=self.descricao,
            status=self.status,
            questoes=questoes,
        )

    def get_json_respostas_questao(self):
        questoes = [questao.get_json() for questao in self.questoes_pesquisas.all()]
        return dict(
            id=self.pk,
            descricao=self.descricao,
            status=self.status,
            questoes=questoes,
        )


'''
classe utilizada para criar as questões, a descriação da questão, independete de está vinculada a uma pesquisa, 
com isso, pode-se usar essa mesma questão e pesquisas diferentes.
'''


class Questao(TimestampableMixin):
    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    descricao = models.CharField(u'Descrição', max_length=255)

    def get_json(self):
        return dict(
            id=self.pk,
            descricao=self.descricao,
        )

    def __str__(self):
        return self.descricao


'''
Classe responsável para vincular a questão com a pesquisa.
a pesquisa poderá ter no máximo 5 questoes vinculada a ela.

Foram criados métodos para calcular a informção do Valor NPS e detalhe das pontuações (detratores, passivos e promotores)

Poderia ter criado variaveis fixas para qunado mudar o status da pesquisa para FINALIZADA, alimentar esses dados, 
dessa segunda forma, teria uma melhor performasse pois não precisaria toda vez realizada a consulta.

'''


class QuestaoPesquisa(TimestampableMixin):
    class Meta:
        unique_together = (("pesquisa", "questao",),)
        verbose_name = 'Questao da Pesquisa'
        verbose_name_plural = 'Questões da Pesquisa'

    pesquisa = models.ForeignKey(Pesquisa, on_delete=models.CASCADE, related_name='questoes_pesquisas')
    questao = models.ForeignKey(Questao, on_delete=models.PROTECT, verbose_name='Questão')

    @property
    def get_detradores(self):
        if self.get_total_respostas == 0:
            return 0
        return (self.respostas.filter(peso__in=[0, 1, 2, 3, 4, 5, 6]).count() / self.get_total_respostas) * 100

    @property
    def get_passivos(self):
        if self.get_total_respostas == 0:
            return 0
        return (self.respostas.filter(peso__in=[7, 8]).count() / self.get_total_respostas) * 100

    @property
    def get_promotores(self):
        if self.get_total_respostas == 0:
            return 0
        return (self.respostas.filter(peso__in=[9, 10]).count() / self.get_total_respostas) * 100

    @property
    def get_total_respostas(self):
        return self.respostas.count()

    @property
    def get_media(self):
        pedo_media = self.respostas.all().aggregate(Sum('peso'))['peso__sum']
        if pedo_media is None:
            return 0
        return pedo_media / self.get_total_respostas

    @property
    def get_valor_NPS(self):
        nps = 0
        if self.get_total_respostas > 0:
            detradores_porc = self.get_detradores
            promotores_porc = self.get_promotores
            sub_detradores_promotores = promotores_porc - detradores_porc
            nps = sub_detradores_promotores
        return nps

    def __str__(self):
        return '{} - {}'.format(self.pesquisa.descricao, self.questao.descricao)

    def get_json(self):
        if self.pesquisa.status == FINALIZADA:
            return dict(
                descricao=self.questao.descricao,
                total_respostas=self.get_total_respostas,
                media=self.get_media,
                detratores='{}.2f%'.format(self.get_detradores),
                passivos='{}.2f%'.format(self.get_passivos),
                promotores='{}.2f%'.format(self.get_promotores),
                valor_nps='{}.2f%'.format(self.get_valor_NPS),
            )
        return dict(
            descricao=self.questao.descricao,

        )

    def get_json_respostas(self):
        respostas = self.respostas.values('peso').annotate(Count('peso'))
        dados = []
        for resposta in respostas:
            dados.append(
                dict(
                    resposta=resposta['peso'],
                    quantidade_resposta=resposta['peso__count']
                )
            )

        return dict(
            id=self.pk,
            descrição=self.questao.descricao,
            respostas=dados
        )


'''
Essa tabela tem a finalidade ter ter um registro ara cada resposta, outra finalidade dessa tabela seria 
armazenas outros dados, como, usuário pesquisado, data, local da pesquisa, entre outros.
'''


class RespostaQuestaoPesquisa(TimestampableMixin):
    class Meta:
        verbose_name = 'RespostaQuestaoPesquisa'
        verbose_name_plural = 'RespostaQuestaoPesquisa'

    questao_pesquisa = models.ForeignKey(QuestaoPesquisa, on_delete=models.CASCADE, related_name='respostas')
    peso = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    # def __str__(self):
    #     return str(self.peso)
