from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from app_controle_nps.models import Usuario, Pesquisa, Questao


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email', 'senha']


class PesquisaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pesquisa
        fields = ['id', 'descricao', 'status']


class RealizarPesquisaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pesquisa
        fields = ['id', 'descricao', 'status']






