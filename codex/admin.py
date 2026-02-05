from django.contrib import admin
from .models import (
    Operator, Garage, Core, CoreBattleInfo, CoreUpgradeInfo,
    Move, Equipment, ImageAsset, CoreEquippedMove, Scrapyard
)


class OperatorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'call_sign', 'rank',)
    search_fields = ('call_sign',)


class MoveAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'dmg_type', 'dmg',
                    'accuracy', 'core_type_identity',)
    search_fields = ('name', 'type', "core_type_identity",)


admin.site.register(Operator, OperatorAdmin)
admin.site.register(Garage)
admin.site.register(Core)
admin.site.register(CoreBattleInfo)
admin.site.register(CoreUpgradeInfo)
admin.site.register(Move, MoveAdmin)
admin.site.register(Equipment)
admin.site.register(ImageAsset)
admin.site.register(CoreEquippedMove)
admin.site.register(Scrapyard)
