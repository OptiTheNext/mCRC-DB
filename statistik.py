import flask
import random
import mysql.connector
import datetime
import Columns
import os
from dotenv import load_dotenv
import pandas
import numpy
import matplotlib
import requests
import string
import json
from flask_session import Session
from flask import Flask, session
from mailjet_rest import Client
import jwt


def deskreptiv(df):
    print("Wuhu, statistik")
