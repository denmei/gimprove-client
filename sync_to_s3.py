import os
from pathlib import Path

os.chdir(str(Path(os.path.dirname(os.path.realpath(__file__)))))
os.system("aws s3 sync client_repo "
          "s3://client-repository "
          "--exclude '*/.credentials.json' "
          "--exclude 'test/*' "
          "--exclude '*/config.json' "
          "--exclude '.idea/*' "
          "--exclude */weight_translation.csv "
          "--exclude '*logs/*' "
          "--exclude '*__pycache__/*' "
          "--exclude */client_cache.json "
          "--exclude 'weights.csv' "
          "--exclude=distances.csv "
          "--exclude 'README.md' "
          "--exclude 'readme/*' ")