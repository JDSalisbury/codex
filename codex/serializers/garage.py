

from rest_framework import serializers
from codex.models import Garage, GarageMoveLibrary
from codex.serializers.move import MoveListSerializer


class GarageMoveLibrarySerializer(serializers.ModelSerializer):
    """Serializer for garage move library entries"""
    move = MoveListSerializer(read_only=True)

    class Meta:
        model = GarageMoveLibrary
        fields = ['id', 'move', 'copies_owned', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GarageSerializer(serializers.ModelSerializer):
    active_cores_count = serializers.SerializerMethodField()
    has_capacity = serializers.SerializerMethodField()
    move_library_entries = GarageMoveLibrarySerializer(
        source='garagemovelibrary_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Garage
        fields = '__all__'

    def get_active_cores_count(self, obj):
        """Return count of non-decommissioned cores in this garage."""
        return obj.cores.filter(decommed=False).count()

    def get_has_capacity(self, obj):
        """Return whether garage has room for more cores."""
        return obj.has_capacity()
