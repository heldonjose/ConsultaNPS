from django.contrib.auth import authenticate
from rest_framework import status, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_controle_nps.models import Pesquisa, Questao
from app_controle_nps.serializers import UsuarioSerializer, PesquisaSerializer, RealizarPesquisaSerializer
from rest_framework.authtoken.models import Token

from util.choicesModels import PESQUISADOR, INICIADA, CRIADA, FINALIZADA
from django.shortcuts import get_object_or_404


class IsAutenticatedListApiView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([TokenAuthentication])


class PesquisadorAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        token = self.get_model().objects.select_related('user').get(key=key)
        if token.user.usuario.tipo != PESQUISADOR:
            responser = dict(detail="Usuário sem permissão.")
            raise exceptions.AuthenticationFailed(responser)
        return super().authenticate_credentials(key)


class LoginView(GenericAPIView):
    serializer_class = UsuarioSerializer

    def post(self, request):
        print('asas')
        print(request.data)
        user = authenticate(username=request.data['email'], password=request.data['senha'])
        if user is None:
            return Response({"detail": "Usuário ou senha inválido"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        print(token)
        return Response(user.usuario.get_json(), status=status.HTTP_200_OK)


def pesquisas_iniciadas_nao_respondidas():
    query = Pesquisa.objects.filter(status=INICIADA)
    for q in query:
        if q.questoes.filter(peso__isnull=False).exists():
            query = query.exclude(id=q.id)
    return query


class PesquisaListView(IsAutenticatedListApiView):
    queryset = Pesquisa.objects.none()
    serializer_class = PesquisaSerializer

    def get_queryset(self):
        usuario = self.request.user.usuario
        if usuario.tipo == PESQUISADOR:
            query = Pesquisa.objects.all()
        else:
            query = pesquisas_iniciadas_nao_respondidas()
        return query


class PesquisaDetalhe(IsAutenticatedListApiView):
    queryset = Pesquisa.objects.none()
    serializer_class = PesquisaSerializer

    def get_queryset(self):
        usuario = self.request.user.usuario
        if usuario.tipo == PESQUISADOR:
            query = Pesquisa.objects.all()
        else:
            query = Pesquisa.objects.filter(status=INICIADA)
        return query


class IniciarPesquisa(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([PesquisadorAuthentication])

    def get(self, request, pk):
        print('get')
        pesquisa = Pesquisa.objects.get(pk=pk)

        if pesquisa.status == INICIADA:
            return Response({'detail': "Pesquisa já foi Iniciada em {}".format(pesquisa.data_cadastro)},
                            status=status.HTTP_401_UNAUTHORIZED)
        if pesquisa.status == FINALIZADA:
            return Response({'detail': "Pesquisa já finalizada".format(pesquisa.data_cadastro)},
                            status=status.HTTP_401_UNAUTHORIZED)

        pesquisa.status = INICIADA
        pesquisa.save()
        return Response({'detail': "Pesquisa Iniciada"}, status=status.HTTP_200_OK)


class FinalizarPesquisa(GenericAPIView):
    serializer_class = RealizarPesquisaSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([TokenAuthentication])


class RealizarPesquisa(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([PesquisadorAuthentication])

    def get(self, request, pk):
        print('get')
        pesquisa = Pesquisa.objects.get(pk=pk)
        # pesquisa = Pesquisa.objects.get(pk=pk)

        if pesquisa.status == CRIADA:
            return Response({'detail': "Pesquisa ainda não foi iniciada"},
                            status=status.HTTP_401_UNAUTHORIZED)
        if pesquisa.status == FINALIZADA:
            return Response({'detail': "Pesquisa já foi finalizada"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if pesquisa.questoes.filter(peso__isnull=True):
            return Response({'detail': "Pesquisa com respostas pendentes"},
                            status=status.HTTP_401_UNAUTHORIZED)

        pesquisa.status = FINALIZADA
        pesquisa.save()
        return Response({'detail': "Pesquisa Finalizada"}, status=status.HTTP_200_OK)


class PesquisaDetalhe(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([TokenAuthentication])

    def get(self, request, pk):
        print('get')
        # pesquisa = Pesquisa.objects.get_object_or_404(pk=pk)
        pesquisa = get_object_or_404(Pesquisa, pk=pk)
        print(pesquisa)
        usuario = self.request.user.usuario

        if usuario.tipo == PESQUISADOR:
            dados = pesquisa.get_json_detalheNPS()
        else:
            if pesquisa.status == FINALIZADA or pesquisa.status == CRIADA:
                return Response({'detail': "Usuário sem acesso a essa pesquisa"}, status=status.HTTP_401_UNAUTHORIZED)
            if pesquisa.questoes.filter(peso__isnull=False).exists():
                return Response({'detail': "Pesquisa já foi iniciada, usuário sem acesso"}, status=status.HTTP_401_UNAUTHORIZED)
            dados = pesquisa.get_json()
        return Response(dados, status=status.HTTP_200_OK)


class ListaRespostasPesquisaFinalizadaListView(GenericAPIView):
    authentication_classes = ([PesquisadorAuthentication])

    def get(self, request):
        pesquisas = [pesquisa.get_json() for pesquisa in Pesquisa.objects.filter(status=FINALIZADA)]
        return Response(pesquisas, status=status.HTTP_200_OK, )
