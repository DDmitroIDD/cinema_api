from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from api.q_sets import q_set
from api.models import CustomUser, CinemaHall, MovieSeance, Buying


class CustomUserSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'avatar', 'password_confirmation')
        write_only_fields = ('password', )
        read_only_fields = ('id',)

    def validate(self, data):
        if self.context['request'].user.is_anonymous:
            if data['password'] != data.pop('password_confirmation'):
                raise serializers.ValidationError('Passwords do not match!')
            return data
        raise serializers.ValidationError('You are already registered!')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class MovieSeanceSerializer(TaggitSerializer, serializers.ModelSerializer):
    start_time_seance = serializers.TimeField(required=True)
    end_time_seance = serializers.TimeField(required=True)
    show_start_date = serializers.DateTimeField(required=True)
    show_end_date = serializers.DateTimeField(required=True)
    price = serializers.IntegerField(required=True)
    tag = TagListSerializerField(required=True)
    show_hall = serializers.SlugRelatedField(slug_field="hall_name", queryset=CinemaHall.objects.all())

    class Meta:
        model = MovieSeance
        fields = ('id', 'movie_title', 'show_hall', 'tag', 'image', 'slug',
                  'start_time_seance', 'end_time_seance',
                  'show_start_date', 'show_end_date', 'price', 'free_seats')
        read_only_fields = ('id', 'free_seats', )
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def create(self, validated_data):
        validated_data['free_seats'] = CinemaHall.objects.get(id=validated_data['show_hall'].id).hall_size
        validated_data['slug'] = '_'.join(validated_data['movie_title'].split())
        movie = MovieSeance.objects.create(**validated_data)
        return movie

    def validate(self, attrs):
        movies = False
        show_hall = attrs.get('show_hall', False)
        start_time = attrs.get('start_time_seance', False)
        end_time = attrs.get('end_time_seance', False)
        start_date = attrs.get('show_start_date', False)
        end_date = attrs.get('show_end_date', False)
        if all((start_time, start_date, end_date, end_time, show_hall)):
            q = q_set(start_time, end_time, start_date, end_date)
            movies = CinemaHall.objects.get(id=show_hall.pk).movies.filter(q[0] | q[1] | q[4], q[2] | q[3] | q[5])
        if self.instance:
            movie = self.instance
            purchases = Buying.objects.filter(movie=movie)
            if purchases:
                raise serializers.ValidationError(
                    {'update_movie_error': 'Tickets for this session have already been purchased, cannot be changed!'})
            if movies:
                movies = movies.exclude(id=movie.pk)

        if all((start_time, end_time, start_time > end_time)):
            raise serializers.ValidationError({'time_error': 'Start time cannot be later than end time!'})
        elif all((start_date, end_date, start_date > end_date)):
            raise serializers.ValidationError({'date_error': 'Start date cannot be later than end date'})
        if movies:
            raise serializers.ValidationError(
                {'datetime_error': 'This day and this time the hall is busy! Choose another time or date!'})
        return attrs


class CinemaHallSerializer(serializers.ModelSerializer):
    movies = MovieSeanceSerializer(many=True, required=False)
    hall_size = serializers.IntegerField(required=True)

    class Meta:
        model = CinemaHall
        fields = ('id', 'hall_name', 'hall_size', 'movies', )
        read_only_fields = ('id', 'movies', )

    def validate(self, attrs):
        if self.instance:
            cinema_hall_id = self.instance.id
            hall_size = self.instance.hall_size
            movies = CinemaHall.objects.get(id=cinema_hall_id).movies.filter(free_seats__lt=hall_size)
            if movies:
                raise serializers.ValidationError(
                            {'movies': 'There are purchased tickets in this hall, cannot be changed!'})
            hall_size = attrs['hall_size']
            CinemaHall.objects.get(id=cinema_hall_id).movies.all().update(free_seats=hall_size)
        return attrs


class BuyingSerializer(serializers.ModelSerializer):
    qnt = serializers.IntegerField(required=True)
    spent = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(slug_field="username", queryset=CustomUser.objects.all())

    class Meta:
        model = Buying
        fields = ('id', 'spent', 'user', 'movie', 'qnt')
        read_only_fields = ('id', 'spent', 'user', )
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def get_spent(self, obj):
        return obj.user.spent

    def validate(self, attrs):
        movie = MovieSeance.objects.get(id=attrs['movie'].id)
        user = CustomUser.objects.get(id=self.context['request'].user.id)
        qnt = attrs['qnt']
        if (movie.free_seats - qnt) < 0:
            raise serializers.ValidationError({'qnt': 'Not enough free seats!'})
        movie.free_seats -= qnt
        user.spent += qnt * movie.price
        movie.save()
        user.save()
        attrs['user'] = user
        return attrs


class ContactSerailizer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()
