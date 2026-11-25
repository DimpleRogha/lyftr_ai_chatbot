from llm import router

print("Configured deployments:")

for deployment in router.model_list:
    print(
        deployment["model_info"]["id"],
        deployment["litellm_params"]["order"]
    )