from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from pathlib import Path
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from photo_utils import save_user_photo
from docs_processing import process_document
from open_ai_processing import ask_openai
from dotenv import load_dotenv
import os

##########################################################################################
load_dotenv()
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
app = (ApplicationBuilder().token(TELEGRAM_API_KEY).build())
##########################################################################################


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "🚗 Start Car Insurance", callback_data="start_insurance"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Hi {update.effective_user.first_name}!\n\n"
        "I'm your Car Insurance Assistant Bot. I can help you choose and buy car insurance easily.",
        reply_markup=reply_markup,
    )


######################################################################################################
# Working with the button prress
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "start_insurance":
        await query.edit_message_text(
            text="✅ Great! Let's begin with your car insurance process 🚗📝"
        )
        # here we add an answer from openAI
        response = await ask_openai("explain the car insurance process in simple English")
        await query.message.reply_text(response)
        # set the user state
        context.user_data["stage"] = "waiting_for_drivers_licence_photo"
        await query.message.reply_text(
            "Please submit a photo of your driver's licence."
        )

    elif query.data in ["price_confirm_yes", "price_confirm_no"]:
        await handle_price_confirmation(update, context)


################################################################################################
# working with photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("stage")

    if update.message.photo:
        file_path = await save_user_photo(update.message.photo, context.bot)

        if stage == "waiting_for_drivers_licence_photo":
            context.user_data["license_photo_path"] = file_path
            context.user_data["stage"] = "waiting_for_car_photo"
            await update.message.reply_text(
                f"✅ Driver's license photo saved {context.user_data['license_photo_path']}.\n📸"
                "Now send a photo of your car showing the VIN number."
            )

        elif stage == "waiting_for_car_photo":
            context.user_data["car_photo_path"] = file_path
            context.user_data["stage"] = "complete"
            await update.message.reply_text(
                f"✅ Car photo with VIN saved.\n🎉 {context.user_data['car_photo_path']}"
                "All photos received. We will now begin processing your insurance."
            )
            
            await update.message.reply_text(f"We are proceesing your documents... Please wait for 5-10 seconds...")
            await handle_user_confirmation(update, context)
        else:
            await update.message.reply_text(
                "❗Unexpected stage. Please start the insurance process again."
            )

    else:
        await update.message.reply_text("❗Please send a valid photo.")


async def handle_user_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message
    if context.user_data["stage"] == "complete":
        # Processing the photos with mindee API 
        drivers_licance_result_document = process_document(context.user_data['license_photo_path'])
        car_result_document = process_document(context.user_data['car_photo_path'])

        await message.reply_text("✅ Your documents have been processed successfully!")
        await message.reply_text("✅ Wait for the processing result ...")
        await message.reply_text(
            "✅ Please confirm the data:\n\n"
             f"🚗 Driver's License:\n{drivers_licance_result_document}\n\n"
             f"🚗 Car Document:\n{car_result_document}\n\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Yes, all is correct", callback_data="confirm_yes"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ No, the data is not correct", callback_data="confirm_no"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "Do you confirm the extracted data?", reply_markup=reply_markup
        )


async def handle_user_confirmation_response(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_yes":
        await query.edit_message_text("✅ Thank you! Let's move to the next step.")
        await proceed_to_price_quotation(query.message, context)
    elif query.data == "confirm_no":
        await query.edit_message_text(
            "❌ Please resubmit your photos to restart the process."
        )
        context.user_data["stage"] = "waiting_for_drivers_licence_photo"
        await query.message.reply_text(
            "Please submit a photo of your driver's licence again."
        )


# inform the user about price
async def proceed_to_price_quotation(message, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Yes, I agree with the price", callback_data="price_confirm_yes"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ No, I don't agree", callback_data="price_confirm_no"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        "💰 The price for the insurance is 100 USD. Do you agree?",
        reply_markup=reply_markup,
    )
    response = await ask_openai("explain why we have this price and why it is good")
    await message.reply_text(response)


# working with user's answer
async def handle_price_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "price_confirm_yes":
        await query.edit_message_text(
            "✅ Thank you! Your insurance will now be processed."
        )

        policy_path = Path(__file__).parent / "company_policy.txt"
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                policy_text = f.read()

            await query.message.reply_text(
                f"📄 *Company Policy Document:*\n\n{policy_text}",
                parse_mode="Markdown"
        )
        except FileNotFoundError as e:
            await query.message.reply_text("❌ Error: Company policy document not found.")
            print(f"FileNotFoundError: {e}")

        keyboard = [
            [InlineKeyboardButton("✅ I agree", callback_data="policy_agree"),
            InlineKeyboardButton("❌ I do not agree", callback_data="policy_disagree"),]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Do you agree with the policy terms?", reply_markup=reply_markup
        )
        # ask open ai
        response = await ask_openai("explain why you have to agree with the policy")
        await query.message.reply_text(response)



        # Proceed to finalization
    elif query.data == "price_confirm_no":
        await query.edit_message_text(
            "❌ Sorry, the price is fixed at 100 USD. Please confirm to proceed."
        )
        await proceed_to_price_quotation(query.message, context)


############################################################################################################
# working with the policy confirmation
async def handle_policy_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "policy_agree":
        await query.edit_message_text("🎉 Thank you for agreeing! Your insurance is now being finalized.")
    elif query.data == "policy_disagree":
        await query.edit_message_text("❌ You must agree to the policy to proceed with the insurance.")
        await show_policy_document(update, context)
        

################################################################################################################

async def show_policy_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send the company policy document again with the buttons for confirmation
    try:
        with open("company_policy.txt", "r") as file:
            policy_text = file.read()
    except FileNotFoundError:
        policy_text = "❗Sorry, we couldn't find the company policy document."

    # Send the document as text (not as a file)
    await update.callback_query.message.reply_text(
        policy_text,
        parse_mode=ParseMode.MARKDOWN 
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ I agree with the policy", callback_data="policy_agree")
        ],
        [
            InlineKeyboardButton("❌ I disagree with the policy", callback_data="policy_disagree")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Re-send the confirmation message with the policy document
    await update.callback_query.message.reply_text(
        "📄 Please read and confirm our company policy document below:\n\nDo you agree?",
        reply_markup=reply_markup
    )


################################################################################################################
if __name__ == '__main__':
    # adding handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(start_insurance|price_confirm_.*)$"))
    app.add_handler(CallbackQueryHandler(handle_user_confirmation_response, pattern="^confirm_"))
    app.add_handler(CallbackQueryHandler(handle_policy_confirmation, pattern="^policy_"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


        # ▶launching the bot
    app.run_polling()
