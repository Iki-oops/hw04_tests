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
        cls.group = Group.objects.create(
            title='Тест',
            slug='test',
            description='Домашние тесты',
        )
        cls.post = Post.objects.create(
            text='ya bobyor',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='YaBobr')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        template_pages_name = {
            'index.html': '/',
            'group.html': f'/group/{PostPagesTest.group.slug}/',
            'new_post.html': '/new/',
            'profile.html': f'/{PostPagesTest.user}/'
        }

        for template, reverse_name in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_list_show_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        get_page = response.context.get('page')[0]
        post_text_0 = get_page.text
        post_author_0 = get_page.author
        post_group_0 = get_page.group
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
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test'}))
        get_group = response.context.get('group')
        group_title = get_group.title
        group_slug = get_group.slug
        group_description = get_group.description
        self.assertEquals(group_title, 'Тест')
        self.assertEquals(group_slug, 'test')
        self.assertEquals(group_description, 'Домашние тесты')

    def test_profile_list_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': PostPagesTest.user}))
        get_page = response.context.get('page')[0]
        profile_text_0 = get_page.text
        profile_author_0 = get_page.author
        profile_group_0 = get_page.group
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
        for i in range(13):
            Post.objects.create(
                id=i,
                text='Ya',
                author=cls.user,
                group=cls.group,
            )

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
