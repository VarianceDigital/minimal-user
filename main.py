from minimaluser import create_app
import os

os.environ["SESSION_SECRET"]="YourSessionSecret"
os.environ["JWT_SECRET_HTML"]="YourHTMLApiSecret"
os.environ["JWT_MAILER_SECRET"]="YourMailerSecret"
os.environ["MAILER_URL"]="https://mymailer.sass.com/"
os.environ["AWS_TILES_BUCKET_NAME"]="my-tiles" #for user tiles
os.environ["AWS_TILES_BUCKET_URL"]="https://my-tiles.s3.eu-west-3.amazonaws.com/" 
os.environ["AWS_ACCESS_KEY"]="YOURAWSACCESSKEY"
os.environ["AWS_SECRET_ACCESS_KEY"]="LongerAWSAccessSecret"

app = create_app()
app.run()

