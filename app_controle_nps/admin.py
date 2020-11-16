from django.contrib import admin
from django.contrib.auth.models import User, Group
from app_controle_nps.models import Usuario, Pesquisa, QuestaoPesquisa, RespostaQuestaoPesquisa, Questao
from util.choicesModels import PESQUISADOR, FINALIZADA, CRIADA

admin.site.register(Questao)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo')
    search_fields = ('nome', 'email')
    exclude = ['user']

    def save_model(self, request, obj, form, change):
        if not change:
            user = User.objects.create(username=obj.email, email=obj.email)
            user.set_password(obj.senha)
            obj.user = user
        else:
            obj.user.username = obj.email
            obj.user.email = obj.email
            obj.user.set_password(obj.senha)
            # obj.user.save()
        if obj.tipo == PESQUISADOR:
            obj.user.is_staff = True
            grupo = Group.objects.get(name='PESQUISADOR')
            obj.user.groups.clear()
            obj.user.groups.add(grupo)
        obj.user.save()
        super().save_model(request, obj, form, change)


class QuestaoInline(admin.TabularInline):
    fields = ['questao', 'get_total_respostas', 'media_geral', 'detradores', 'passivos', 'promotores',
              'get_valor_NPS']
    readonly_fields = ['get_total_respostas', 'media_geral', 'detradores', 'passivos', 'promotores',
                       'get_valor_NPS']
    model = QuestaoPesquisa
    max_num = 5
    verbose_name_plural = 'Questões da Pesquisa'

    def detradores(self, obj):
        return '{:.2f}%'.format(obj.get_detradores)

    def passivos(self, obj):
        return '{:.2f}%'.format(obj.get_passivos)

    def promotores(self, obj):
        return '{:.2f}%'.format(obj.get_promotores)

    def media_geral(self, obj):
        return '{:.2f}%'.format(obj.get_media)



@admin.register(Pesquisa)
class PesquisaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'status', 'quantidade_questoes')
    list_editable = ['status', ]
    search_fields = ('descricao',)
    exclude = ['status', ]
    inlines = [QuestaoInline]

    def get_list_display_links(self, request, list_display):
        print(list_display)
        return super().get_list_display_links(request, list_display)


    def quantidade_questoes(self, obj):
        return obj.questoes_pesquisas.all().count()

    quantidade_questoes.short_description = u'Quantidade de Questões'


class RespostaQuestaoPesquisaInline(admin.TabularInline):
    model = RespostaQuestaoPesquisa
    extra = 0
    verbose_name_plural = 'Respostas da Questão'


@admin.register(QuestaoPesquisa)
class QuestaoPesquisaPesquisaAdmin(admin.ModelAdmin):
    list_display = (
        'pesquisa', 'status_pesquisa', 'questao', 'total_respostas', 'media_geral', 'detradores',
        'passivos', 'promotores', 'valor_nps')
    list_filter = ('pesquisa', 'questao')
    inlines = [RespostaQuestaoPesquisaInline]

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.pesquisa.status == FINALIZADA or obj.pesquisa.status == CRIADA:
                return False
        return True

    def status_pesquisa(self, obj):
        return '{}'.format(obj.pesquisa.status)

    def total_respostas(self, obj):
        return '{}'.format(obj.get_total_respostas)

    def media_geral(self, obj):
        return '{:.2f}'.format(obj.get_media)

    def valor_nps(self, obj):
        return '{}'.format(obj.get_valor_NPS)

    def detradores(self, obj):
        return '{:.2f}%'.format(obj.get_detradores)

    def passivos(self, obj):
        return '{:.2f}%'.format(obj.get_passivos)

    def promotores(self, obj):
        return '{:.2f}%'.format(obj.get_promotores)
