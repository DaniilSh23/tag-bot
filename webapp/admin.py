from django.contrib import admin

from webapp.models import BotUser, BotSettings, PaymentBills, Transaction, Profiles, GroupChats, GroupChatFiles


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "key",
        "value",
    )
    list_display_links = (
        "pk",
        "key",
        "value",
    )


class ProfilesInline(admin.TabularInline):
    """
    Класс для инлайн отображения данных из таблицы Profiles на детальной странице BotUsers
    """
    model = Profiles
    fields = ('balance',)
    verbose_name = 'профиль'
    verbose_name_plural = 'профили'
    # readonly_fields = ('balance',)
    extra = 3


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "tlg_id",
        "tlg_username",
        "balance",
        "start_bot_at",
    )
    list_display_links = (
        "pk",
        "tlg_id",
        "tlg_username",
        "balance",
        "start_bot_at",
    )
    inlines = [ProfilesInline]  # Добавляем вложенный класс

    def balance(self, obj):
        return obj.profiles.balance

    balance.short_description = 'Balance'


@admin.register(PaymentBills)
class PaymentBillsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "bot_user",
        "amount",
        "created_at",
        "pay_method",
        "status",
        "file",
    )
    list_display_links = (
        "pk",
        "bot_user",
        "amount",
        "created_at",
        "pay_method",
        "status",
    )
    list_filter = (
        "pay_method",
        "status",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'bot_user',
        'amount',
        'operation_type',
        'created_at',
        'short_description',
    )
    list_display_links = (
        'pk',
        'bot_user',
        'amount',
        'operation_type',
        'created_at',
        'short_description',
    )
    list_filter = (
        "operation_type",
    )

    def short_description(self, obj: Transaction):
        """
        Метод для преобразования описания в сокращённый вариант.
        """
        return obj.description if len(obj.description) < 48 else f"{obj.description[:48]}..."


@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'bot_user',
        'balance',
    )
    list_display_links = (
        'pk',
        'bot_user',
        'balance',
    )


class GroupChatFilesInline(admin.StackedInline):
    model = GroupChatFiles


@admin.register(GroupChats)
class GroupChatsAdmin(admin.ModelAdmin):
    inlines = (
        GroupChatFilesInline,
    )
    list_display = (
        'pk',
        'bot_user',
        'group_tg_id',
        'tag_now',
        'bot_rights_checked',
        'in_work',
        'paid_by',
        'created_at',
    )
    list_display_links = (
        'pk',
        'bot_user',
        'group_tg_id',
        'tag_now',
        'bot_rights_checked',
        'in_work',
        'paid_by',
        'created_at',
    )


@admin.register(GroupChatFiles)
class GroupChatFilesAdmin(admin.ModelAdmin):
    """
    Регистрируем в админке модель GroupChatFiles
    """
    list_display = (
        'pk',
        'file_name',
        'group_chat',
    )
    list_display_links = (
        'pk',
        'file_name',
        'group_chat',
    )