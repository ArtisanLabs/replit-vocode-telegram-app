import base64
import inspect
import io
import logging
import os
import pickle
import re
from collections import defaultdict
from typing import Dict, Optional, Tuple, Type, Union

import vocode
from pydub import AudioSegment
from replit import db
from telegram import Update 
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

