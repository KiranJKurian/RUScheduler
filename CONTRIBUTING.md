# How to Contribute

Want to add a new feature or fix a typo? Great, here's how to do that:

 - Fork the repository (button in top right)
 - Go to your copy of the repo and copy the URL - `git clone {repo url}`
 - Add repo as upstream - `git remote add upstream https://github.com/GrandmasterK/RUScheduler.git`
 make changes on a branch - `git checkout -b {new feature}`
 - commit changes - `git commit -am "cool feature"`
 - push them back to github - `git push`
 - Make a pull request from github's web interface
 - After merge, delete branch - `git branch -D {new feature}`


 **To update your local copy of the repo (when upstream changes):**

  - `git fetch upstream`
  - `git merge upstream/master`
  - `git push`