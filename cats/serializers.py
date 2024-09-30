from rest_framework import serializers
import datetime as dt
import webcolors

from .models import Cat, Owner, Achievement, AchievementCat, CHOICES


class AchievementSerializer(serializers.ModelSerializer):
    # Переопределение поля и применение параметра source со старым именем из модели
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatListSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=CHOICES)
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color') 


class CatSerializer(serializers.ModelSerializer):
    # Переопределяем поле achievements. Назначьте типом поля achievements сериализатор AchievementSerializer. Да, так можно!
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
    # Теперь поле примет только значение, упомянутое в списке CHOICES
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year',
                  'owner', 'achievements', 'age')

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        # Если в исходном запросе не было поля achievements
        if 'achievements' not in self.initial_data:
            # То создаём запись о котике без его достижений
            cat = Cat.objects.create(**validated_data)
            return cat

        # Уберём список достижений из словаря validated_data и сохраним его
        achievements = validated_data.pop('achievements')

        # Создадим нового котика пока без достижений, данных нам достаточно
        cat = Cat.objects.create(**validated_data)

        # Для каждого достижения из списка достижений
        for achievement in achievements:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement)
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat)
        return cat


class OwnerSerializer(serializers.ModelSerializer):
    # Роль StringRelatedField — получить строковые представления связанных объектов и передать их в указанное поле вместо id.
    # Поля с типом StringRelatedField не поддерживают операции записи, поэтому для них всегда должен быть указан параметр read_only=True.
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')
