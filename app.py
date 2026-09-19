import os
from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = user=os.getenv("SECRET_KEY")