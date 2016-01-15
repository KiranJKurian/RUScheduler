git pull
git add -A
git commit -m "$*"
git push -u origin master
curl -S http://ruscheduler.com/updateSelf/
