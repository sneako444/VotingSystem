# tests/test_selenium.py
import os
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from votes.models import Candidate, Vote, Result

class VotingSystemSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()
        cls.browser.implicitly_wait(5)
        
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Create test data
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_active=True
        )
        
        self.candidate1 = Candidate.objects.create(
            title='Mr.',
            name='John Doe',
            description='Experienced leader',
            photo='candidates/john.jpg'
        )
        
        self.candidate2 = Candidate.objects.create(
            title='Ms.',
            name='Jane Smith',
            description='Innovative thinker',
            photo='candidates/jane.jpg'
        )
        
        Result.objects.create(candidate=self.candidate1, votes_count=0)
        Result.objects.create(candidate=self.candidate2, votes_count=0)
    
    def tearDown(self):
        # Clean up test data
        Vote.objects.all().delete()
        Result.objects.all().delete()
        Candidate.objects.all().delete()
        User.objects.all().delete()
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Helper method to wait for an element"""
        try:
            return WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException as e:
            print(f"\nElement not found: {selector}")
            print("Current URL:", self.browser.current_url)
            print("Page source:", self.browser.page_source[:1000])
            raise e
    def test_1_user_registration(self):
        """Test new user can register"""
        self.browser.get(f"{self.live_server_url}/register")
        
        # Fill registration form
        username = self.wait_for_element('#id_username')
        username.send_keys('newuser')
        
        password1 = self.browser.find_element(By.ID, 'id_password1')
        password1.send_keys('complexpass123')
        
        password2 = self.browser.find_element(By.ID, 'id_password2')
        password2.send_keys('complexpass123')
        
        # Submit form
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Verify redirect to login page
        self.wait_for_element('#username')
        self.assertIn('login', self.browser.current_url)
    
    def test_2_user_login(self):
        """Test registered user can login"""
        self.browser.get(f"{self.live_server_url}/login")
        
        # Fill login form
        username = self.wait_for_element('#username')
        username.send_keys('testuser')
        
        password = self.browser.find_element(By.ID, 'password')
        password.send_keys('testpass123')
        
        # Submit form
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Verify redirect to voting page and candidate cards are visible
        self.wait_for_element('.card')
        self.assertIn('vote', self.browser.current_url)
    
    def test_3_voting_process(self):
        """Test user can vote for a candidate"""
        # First login
        self.test_2_user_login()
        
        # Find and click vote button for first candidate
        vote_buttons = self.wait_for_element('.vote-btn')
        first_vote_button = self.browser.find_elements(By.CSS_SELECTOR, '.vote-btn')[0]
        first_vote_button.click()
        
        # Verify vote was recorded
        self.wait_for_element('.alert-success')
        success_message = self.browser.find_element(By.CSS_SELECTOR, '.alert-success').text
        self.assertIn('recorded', success_message.lower())
        
        # Verify button is now disabled
        disabled_button = self.browser.find_elements(By.CSS_SELECTOR, '.btn-success')[0]
        self.assertFalse(disabled_button.is_enabled())
    
    def test_4_duplicate_vote_prevention(self):
        """Test user cannot vote twice for same candidate"""
        # First vote
        self.test_3_voting_process()
        
        # Try to vote again
        disabled_button = self.browser.find_elements(By.CSS_SELECTOR, '.btn-success')[0]
        disabled_button.click()
        
        # Verify warning message
        self.wait_for_element('.alert-warning')
        warning_message = self.browser.find_element(By.CSS_SELECTOR, '.alert-warning').text
        self.assertIn('already voted', warning_message.lower())
    
    def test_5_results_display(self):
        """Test results are displayed correctly"""
        # Create some votes
        Vote.objects.create(user=self.test_user, candidate=self.candidate1)
        Vote.objects.create(user=self.test_user, candidate=self.candidate2)
        
        # Publish results
        result1 = Result.objects.get(candidate=self.candidate1)
        result1.votes_count = 1
        result1.is_published = True
        result1.save()
        
        result2 = Result.objects.get(candidate=self.candidate2)
        result2.votes_count = 1
        result2.is_published = True
        result2.save()
        
        # View results page
        self.browser.get(f"{self.live_server_url}results/")
        
        # Verify results table
        table = self.wait_for_element('.table-striped')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertGreaterEqual(len(rows), 2)  # Header + at least 1 result row
        
        # Verify progress bars
        progress_bars = self.browser.find_elements(By.CSS_SELECTOR, '.progress-bar')
        self.assertGreaterEqual(len(progress_bars), 1)
    
    def test_6_admin_result_publishing(self):
        """Test admin can publish results"""
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        
        # Login as admin
        self.browser.get(f"{self.live_server_url}/login")
        self.wait_for_element('#username').send_keys('admin')
        self.browser.find_element(By.ID, 'password').send_keys('adminpass')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Go to admin dashboard
        self.browser.get(f"{self.live_server_url}/admin/")
        
        # Login to admin interface (again)
        if 'admin/login' in self.browser.current_url:
            self.wait_for_element('#id_username').send_keys('admin')
            self.browser.find_element(By.ID, 'id_password').send_keys('adminpass')
            self.browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        
        # Navigate to results
        self.wait_for_element('a[href="/admin/votes/result/"]').click()
        
        # Select and publish results
        self.wait_for_element('#action-toggle').click()
        self.browser.find_element(By.NAME, 'action').send_keys('publish_results')
        self.browser.find_element(By.NAME, 'index').click()
        
        # Verify results were published
        published_results = Result.objects.filter(is_published=True)
        self.assertEqual(published_results.count(), 2)

