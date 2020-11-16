from django.urls import path, include
from app_controle_nps.views import LoginView, PesquisaListView, IniciarPesquisa, FinalizarPesquisa, PesquisaDetalhe, \
    RespostasPesquisaListView

urlpatterns = [
    path("login_usuario/", LoginView.as_view(), name="login_usuario"),
    path("lista_pesquisa/", PesquisaListView.as_view(), name="lista_pesquisa"),
    path("iniciar_pesquisa/<int:pk>", IniciarPesquisa.as_view(), name="iniciar_pesquisa"),
    path("finalizar_pesquisa/<int:pk>", FinalizarPesquisa.as_view(), name="finalizar_pesquisa"),

    path("pesquisa_detalhe/<int:pk>", PesquisaDetalhe.as_view(), name="pesquisa_detalhe"),

    path("pesquisas_finalizadas/", RespostasPesquisaListView.as_view(), name="pesquisas_finalizadas"),
    ]