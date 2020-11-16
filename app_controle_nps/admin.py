from django.contrib import admin
from django.contrib.auth.models import User
from app_controle_nps.models import Usuario, Pesquisa, QuestaoPesquisa, RespostaQuestaoPesquisa
from util.choicesModels import PESQUISADOR


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
        obj.user.save()
        super().save_model(request, obj, form, change)


class QuestaoInline(admin.TabularInline):
    model = QuestaoPesquisa
    max_num = 5


@admin.register(Pesquisa)
class PesquisaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'status',)
    list_editable = ['status', ]
    search_fields = ('descricao',)
    exclude = ['status', ]
    inlines = [QuestaoInline]


class RespostaQuestaoPesquisaInline(admin.TabularInline):
    model = RespostaQuestaoPesquisa
    extra = 0


@admin.register(QuestaoPesquisa)
class QuestaoPesquisaPesquisaAdmin(admin.ModelAdmin):
    list_display = (
        'pesquisa', 'questao', 'get_total_respostas', 'get_media', 'detradores', 'passivos', 'promotores', 'valor_nps')
    list_filter = ('pesquisa', 'questao')
    inlines = [RespostaQuestaoPesquisaInline]

    def detradores(self, obj):
        return '{}%'.format(obj.get_detradores)

    def passivos(self, obj):
        return '{}%'.format(obj.get_passivos)

    def promotores(self, obj):
        return '{}%'.format(obj.get_promotores)


    def detradores(self, obj):
        return '{}%'.format(obj.get_detradores)

    def valor_nps(self, obj):
        return '{}%'.format(obj.get_valor_NPS)
