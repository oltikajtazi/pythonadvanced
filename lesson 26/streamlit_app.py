import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(
    page_title="Online Recipe Book",
    page_icon="🍲",
    layout="wide"
)


def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=5,
            **kwargs
        )

        if not response.ok:
            try:
                detail = response.json().get(
                    "detail",
                    response.text
                )
            except ValueError:
                detail = response.text

            st.error(
                f"Error {response.status_code}: {detail}"
            )
            return None

        if response.status_code == 204:
            return {}

        return response.json()

    except requests.RequestException:
        st.error(
            "Cannot connect to the API. "
            "Please start the FastAPI server first."
        )
        return None


def load_categories():
    result = api_request("GET", "/categories/")
    return result if result is not None else []


def load_recipes():
    result = api_request("GET", "/recipes/")
    return result if result is not None else []


st.title("🍲 Online Recipe Book")
st.write(
    "Store, organize, and manage your favorite recipes."
)

with st.sidebar:
    st.header("Navigation")

    page = st.radio(
        "Choose a page",
        [
            "Dashboard",
            "Manage Recipes",
            "Manage Categories"
        ]
    )

    if st.button("Refresh Data"):
        st.rerun()


# DASHBOARD
if page == "Dashboard":
    categories = load_categories()
    recipes = load_recipes()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Recipes", len(recipes))
    col2.metric("Total Categories", len(categories))

    average_time = (
        round(
            sum(r["cooking_time"] for r in recipes)
            / len(recipes)
        )
        if recipes else 0
    )

    col3.metric(
        "Average Cooking Time",
        f"{average_time} min"
    )

    st.subheader("All Recipes")

    if recipes:
        st.dataframe(
            [
                {
                    "ID": r["id"],
                    "Title": r["title"],
                    "Category": (
                        r["category_name"] or "Uncategorized"
                    ),
                    "Cooking Time (min)": r["cooking_time"],
                    "Ingredients": r["ingredients"],
                    "Instructions": r["instructions"]
                }
                for r in recipes
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No recipes yet. Add your first recipe "
            "under Manage Recipes."
        )

    st.subheader("All Categories")

    if categories:
        st.dataframe(
            [
                {
                    "ID": c["id"],
                    "Name": c["name"],
                    "Description": c["description"]
                }
                for c in categories
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No categories yet. Create one under Manage Categories."
        )


# MANAGE CATEGORIES
elif page == "Manage Categories":
    st.header("📁 Manage Categories")

    categories = load_categories()

    create_tab, edit_tab, delete_tab = st.tabs(
        [
            "Create Category",
            "Edit Category",
            "Delete Category"
        ]
    )

    with create_tab:
        with st.form("create_category_form"):
            name = st.text_input("Category Name")
            description = st.text_area("Description")

            submitted = st.form_submit_button(
                "Create Category"
            )

            if submitted:
                if not name.strip():
                    st.warning(
                        "Please enter a category name."
                    )
                else:
                    result = api_request(
                        "POST",
                        "/categories/",
                        json={
                            "name": name.strip(),
                            "description": description.strip()
                        }
                    )

                    if result is not None:
                        st.success(
                            "Category created successfully!"
                        )
                        st.rerun()

    with edit_tab:
        if categories:
            category_map = {
                f"{c['name']} (ID: {c['id']})": c
                for c in categories
            }

            label = st.selectbox(
                "Choose a category to edit",
                list(category_map.keys()),
                key="edit_category"
            )

            category = category_map[label]

            with st.form("edit_category_form"):
                new_name = st.text_input(
                    "Category Name",
                    value=category["name"]
                )

                new_description = st.text_area(
                    "Description",
                    value=category["description"] or ""
                )

                submitted = st.form_submit_button(
                    "Save Changes"
                )

                if submitted:
                    result = api_request(
                        "PUT",
                        f"/categories/{category['id']}",
                        json={
                            "name": new_name.strip(),
                            "description": new_description.strip()
                        }
                    )

                    if result is not None:
                        st.success("Category updated!")
                        st.rerun()
        else:
            st.info("Create a category before editing.")

    with delete_tab:
        if categories:
            category_map = {
                f"{c['name']} (ID: {c['id']})": c
                for c in categories
            }

            label = st.selectbox(
                "Choose a category to delete",
                list(category_map.keys()),
                key="delete_category"
            )

            category = category_map[label]

            st.warning(
                "Recipes in this category will become uncategorized."
            )

            confirmed = st.checkbox(
                "I confirm that I want to delete this category."
            )

            if st.button("Delete Category", type="primary"):
                if not confirmed:
                    st.warning("Please confirm the deletion.")
                else:
                    result = api_request(
                        "DELETE",
                        f"/categories/{category['id']}"
                    )

                    if result is not None:
                        st.success("Category deleted!")
                        st.rerun()
        else:
            st.info("There are no categories to delete.")


# MANAGE RECIPES
elif page == "Manage Recipes":
    st.header("🍽️ Manage Recipes")

    categories = load_categories()
    recipes = load_recipes()

    category_options = {
        f"{c['name']} (ID: {c['id']})": c["id"]
        for c in categories
    }

    category_labels = [
        "Uncategorized"
    ] + list(category_options.keys())

    create_tab, edit_tab, delete_tab = st.tabs(
        [
            "Add Recipe",
            "Edit Recipe",
            "Delete Recipe"
        ]
    )

    with create_tab:
        with st.form("create_recipe_form"):
            title = st.text_input("Recipe Title")

            ingredients = st.text_area(
                "Ingredients",
                placeholder="2 eggs\n1 cup flour\n1 cup milk"
            )

            instructions = st.text_area(
                "Instructions",
                placeholder="1. Prepare ingredients\n2. Cook the recipe"
            )

            cooking_time = st.number_input(
                "Cooking Time (minutes)",
                min_value=0,
                value=30,
                step=5
            )

            category_label = st.selectbox(
                "Category",
                category_labels,
                key="create_recipe_category"
            )

            submitted = st.form_submit_button("Add Recipe")

            if submitted:
                if (
                    not title.strip()
                    or not ingredients.strip()
                    or not instructions.strip()
                ):
                    st.warning(
                        "Please complete the title, ingredients, "
                        "and instructions."
                    )
                else:
                    result = api_request(
                        "POST",
                        "/recipes/",
                        json={
                            "title": title.strip(),
                            "ingredients": ingredients.strip(),
                            "instructions": instructions.strip(),
                            "cooking_time": int(cooking_time),
                            "category_id": category_options.get(
                                category_label
                            )
                        }
                    )

                    if result is not None:
                        st.success("Recipe added successfully!")
                        st.rerun()

    with edit_tab:
        if recipes:
            recipe_map = {
                f"{r['title']} (ID: {r['id']})": r
                for r in recipes
            }

            label = st.selectbox(
                "Choose a recipe to edit",
                list(recipe_map.keys()),
                key="edit_recipe"
            )

            recipe = recipe_map[label]

            current_category = next(
                (
                    name
                    for name, category_id
                    in category_options.items()
                    if category_id == recipe["category_id"]
                ),
                "Uncategorized"
            )

            with st.form("edit_recipe_form"):
                new_title = st.text_input(
                    "Recipe Title",
                    value=recipe["title"]
                )

                new_ingredients = st.text_area(
                    "Ingredients",
                    value=recipe["ingredients"]
                )

                new_instructions = st.text_area(
                    "Instructions",
                    value=recipe["instructions"]
                )

                new_time = st.number_input(
                    "Cooking Time (minutes)",
                    min_value=0,
                    value=int(recipe["cooking_time"]),
                    step=5
                )

                new_category = st.selectbox(
                    "Category",
                    category_labels,
                    index=category_labels.index(current_category),
                    key="edit_recipe_category"
                )

                submitted = st.form_submit_button(
                    "Save Recipe Changes"
                )

                if submitted:
                    if (
                        not new_title.strip()
                        or not new_ingredients.strip()
                        or not new_instructions.strip()
                    ):
                        st.warning(
                            "Please complete all required fields."
                        )
                    else:
                        result = api_request(
                            "PUT",
                            f"/recipes/{recipe['id']}",
                            json={
                                "title": new_title.strip(),
                                "ingredients": new_ingredients.strip(),
                                "instructions": new_instructions.strip(),
                                "cooking_time": int(new_time),
                                "category_id": category_options.get(
                                    new_category
                                )
                            }
                        )

                        if result is not None:
                            st.success("Recipe updated!")
                            st.rerun()
        else:
            st.info("Add a recipe before editing.")

    with delete_tab:
        if recipes:
            recipe_map = {
                f"{r['title']} (ID: {r['id']})": r
                for r in recipes
            }

            label = st.selectbox(
                "Choose a recipe to delete",
                list(recipe_map.keys()),
                key="delete_recipe"
            )

            recipe = recipe_map[label]

            st.write(f"Selected recipe: **{recipe['title']}**")

            confirmed = st.checkbox(
                "I confirm that I want to delete this recipe.",
                key="confirm_recipe_delete"
            )

            if st.button("Delete Recipe", type="primary"):
                if not confirmed:
                    st.warning("Please confirm the deletion.")
                else:
                    result = api_request(
                        "DELETE",
                        f"/recipes/{recipe['id']}"
                    )

                    if result is not None:
                        st.success("Recipe deleted!")
                        st.rerun()
        else:
            st.info("There are no recipes to delete.")