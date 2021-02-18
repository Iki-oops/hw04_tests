from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms

from posts.models import Group, Post


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='YaBobyor')
        Group.objects.create(
            title='Тест',
            slug='test',
            description='Домашние тесты',
        )
        cls.group = Group.objects.get(slug='test')
        Post.objects.create(
            id=1,
            text='ya bobyor',
            author=cls.user,
            group=cls.group,
        )
        cls.post = Post.objects.get(id=1)

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='YaBobr')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        template_pages_name = {
            'index.html': reverse('index'),
            'group.html': (reverse('group_posts', kwargs={'slug': 'test'})),
            'new_post.html': reverse('new_post'),
            'profile.html': (reverse('profile', kwargs={'username': self.user,})),
        }

        for template, reverse_name in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_list_show_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        self.assertEquals(post_text_0, 'ya bobyor')
        self.assertEquals(post_author_0, PostPagesTest.user)
        self.assertEquals(post_group_0, PostPagesTest.group)

    def test_new_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, excepted in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, excepted)
    
    def test_group_posts_page_show_correct_context(self):
        group = PostPagesTest.group
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test'}))
        group_title = response.context.get('group').title
        group_slug = response.context.get('group').slug
        group_description = response.context.get('group').description
        self.assertEquals(group_title, 'Тест')
        self.assertEquals(group_slug, 'test')
        self.assertEquals(group_description, 'Домашние тесты')


    def test_profile_list_show_correct_context(self):
        response = self.authorized_client.get(reverse('profile', kwargs={'username': PostPagesTest.user}))
        profile_text_0 = response.context.get('page')[0].text
        profile_author_0 = response.context.get('page')[0].author
        profile_group_0 = response.context.get('page')[0].group
        self.assertEquals(profile_text_0, 'ya bobyor')
        self.assertEquals(profile_author_0, PostPagesTest.user)
        self.assertEquals(profile_group_0, PostPagesTest.group)


    def test_created_post_in_index(self):
        response = self.authorized_client.get(reverse('index'))
        post = PostPagesTest.post.group
        self.assertEquals(post, response.context.get('page')[0].group)

    def test_created_post_in_selected_group(self):
        response = self.authorized_client.get('/group/test/')
        post = PostPagesTest.post.group
        self.assertEquals(post, response.context.get('page')[0].group)
    

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тест',
            slug='test',
            description='Домашние тесты',
        )
        cls.group = Group.objects.get(slug='test')
        cls.user = get_user_model().objects.create_user(username='Ya')
        objects = []
        for i in range(13):
            Post.objects.create(
                id=i,
                text='Ya',
                author=cls.user,
                group=cls.group,
            )
            post = Post.objects.get(id=i)
        
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEquals(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEquals(len(response.context.get('page').object_list), 3)
