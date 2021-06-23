# Deployment guide

To deploy to new region, most of the workflow is set up. You mainly need to:
1. Clone deploy-to-eu-west-1.yml with respective region setup
2. Run that action
3. Upload songs and users data
4. Setup personalize
5. Setup Comprehend
6. Wait until personalize finishes initial setup (up to 3 hours)
7. Make sure everything is connected