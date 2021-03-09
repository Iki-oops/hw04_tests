from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='church',
            slug='churches',
            description='bread',
        )
        cls.user = get_user_model().objects.create(username='Ya')
        cls.post = Post.objects.create(
            text='Ya',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create(username='Yarik')
        self.authorized_client = Client()
        self.author_post_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post_client.force_login(StaticURLTests.user)

    def test_urls_status_code(self):
        urls = {
            'index': '/',
            'group': f'/group/{StaticURLTests.group.slug}/',
            'new_post': '/new/',
            'profile': reverse('profile', kwargs={'username': self.user}),
            'post': reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
            'post_edit': reverse(
                'post_edit',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
        }
        for value in urls.values():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEquals(response.status_code, 200)

    def test_url_anonymous(self):
        available_urls = {
            'index': '/',
            'group': '/group/churches/',
            'profile': reverse('profile', kwargs={'username': self.user}),
            'post': reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
        }
        for value in available_urls.values():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEquals(response.status_code, 200)

    def test_url_author_post(self):
        available_urls = {
            'index': '/',
            'group': '/group/churches/',
            'new_post': '/new/',
            'profile': reverse('profile', kwargs={'username': self.user}),
            'post': reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
            'post_edit': reverse(
                'post_edit',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
        }
        for value in available_urls.values():
            with self.subTest(value=value):
                response = self.author_post_client.get(value)
                self.assertEquals(response.status_code, 200)

    def test_url_not_author_post(self):
        available_urls = {
            'index': '/',
            'group': '/group/churches/',
            'new_post': '/new/',
            'profile': reverse(
                'profile',
                kwargs={'username': StaticURLTests.user}
            ),
            'post': reverse('post',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
        }
        for value in available_urls.values():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEquals(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        self.template_url_names = {
            'index.html': '/',
            'group.html': '/group/churches/',
            'new_post.html': '/new/',
            'profile.html': reverse('profile', kwargs={'username': self.user}),
            'post.html': reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
            'post_edit.html': reverse(
                'post_edit',
                kwargs={
                    'username': StaticURLTests.user,
                    'post_id': StaticURLTests.post.id
                }
            ),
        }
        for template, url in self.template_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
