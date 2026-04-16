# Aiogram API Complete Guide

This guide documents all the available methods in the aiogram Bot client for building Telegram bots.

---

## Bot Methods

### `add_sticker_to_set(user_id, name, sticker, request_timeout)`

Use this method to add a new sticker to a set created by the bot. Emoji sticker sets can have up to 200 stickers. Other sticker sets can have up to 120 stickers. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#addstickertoset

Parameters:
    user_id (``int``):
        User identifier of sticker set owner

    name (``str``):
        Sticker set name

    sticker (``InputSticker``):
        A JSON-serialized object with information about the added sticker. If exactly the same sticker had already been added to the set, then the set isn't changed.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `answer_callback_query(callback_query_id, text, show_alert, url, cache_time, request_timeout)`

Use this method to send answers to callback queries sent from `inline keyboards <https://core.telegram.org/bots/features#inline-keyboards>`_. The answer will be displayed to the user as a notification at the top of the chat screen or as an alert. On success, :code:`True` is returned.

 Alternatively, the user can be redirected to the specified Game URL. For this option to work, you must first create a game for your bot via `@BotFather <https://t.me/botfather>`_ and accept the terms. Otherwise, you may use links like :code:`t.me/your_bot?start=XXXX` that open your bot with a parameter.

Source: https://core.telegram.org/bots/api#answercallbackquery

Parameters:
    callback_query_id (``str``):
        Unique identifier for the query to be answered

    text (``str | None``):
        Text of the notification. If not specified, nothing will be shown to the user, 0-200 characters

    show_alert (``bool | None``):
        If :code:`True`, an alert will be shown by the client instead of a notification at the top of the chat screen. Defaults to *false*.

    url (``str | None``):
        URL that will be opened by the user's client. If you have created a :class:`aiogram.types.game.Game` and accepted the conditions via `@BotFather <https://t.me/botfather>`_, specify the URL that opens your game - note that this will only work if the query comes from a `https://core.telegram.org/bots/api#inlinekeyboardbutton <https://core.telegram.org/bots/api#inlinekeyboardbutton>`_ *callback_game* button.

    cache_time (``int | None``):
        The maximum amount of time in seconds that the result of the callback query may be cached client-side. Telegram apps will support caching starting in version 3.14. Defaults to 0.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Otherwise, you may use links like :code:`t.me/your_bot?start=XXXX` that open your bot with a parameter.

---

### `answer_inline_query(inline_query_id, results, cache_time, is_personal, next_offset, button, switch_pm_parameter, switch_pm_text, request_timeout)`

Use this method to send answers to an inline query. On success, :code:`True` is returned.

No more than **50** results per query are allowed.

Source: https://core.telegram.org/bots/api#answerinlinequery

Parameters:
    inline_query_id (``str``):
        Unique identifier for the answered query

    results (``list[InlineQueryResultUnion]``):
        A JSON-serialized array of results for the inline query

    cache_time (``int | None``):
        The maximum amount of time in seconds that the result of the inline query may be cached on the server. Defaults to 300.

    is_personal (``bool | None``):
        Pass :code:`True` if results may be cached on the server side only for the user that sent the query. By default, results may be returned to any user who sends the same query.

    next_offset (``str | None``):
        Pass the offset that a client should send in the next query with the same text to receive more results. Pass an empty string if there are no more results or if you don't support pagination. Offset length can't exceed 64 bytes.

    button (``InlineQueryResultsButton | None``):
        A JSON-serialized object describing a button to be shown above inline query results

    switch_pm_parameter (``str | None``):
        `Deep-linking <https://core.telegram.org/bots/features#deep-linking>`_ parameter for the /start message sent to the bot when user presses the switch button. 1-64 characters, only :code:`A-Z`, :code:`a-z`, :code:`0-9`, :code:`_` and :code:`-` are allowed.

    switch_pm_text (``str | None``):
        If passed, clients will display a button with specified text that switches the user to a private chat with the bot and sends the bot a start message with the parameter *switch_pm_parameter*

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: On success, :code:`True` is returned.

---

### `answer_pre_checkout_query(pre_checkout_query_id, ok, error_message, request_timeout)`

Once the user has confirmed their payment and shipping details, the Bot API sends the final confirmation in the form of an :class:`aiogram.types.update.Update` with the field *pre_checkout_query*. Use this method to respond to such pre-checkout queries. On success, :code:`True` is returned. **Note:** The Bot API must receive an answer within 10 seconds after the pre-checkout query was sent.

Source: https://core.telegram.org/bots/api#answerprecheckoutquery

Parameters:
    pre_checkout_query_id (``str``):
        Unique identifier for the query to be answered

    ok (``bool``):
        Specify :code:`True` if everything is alright (goods are available, etc.) and the bot is ready to proceed with the order. Use :code:`False` if there are any problems.

    error_message (``str | None``):
        Required if *ok* is :code:`False`. Error message in human readable form that explains the reason for failure to proceed with the checkout (e.g. "Sorry, somebody just bought the last of our amazing black T-shirts while you were busy filling out your payment details. Please choose a different color or garment!"). Telegram will display this message to the user.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: **Note:** The Bot API must receive an answer within 10 seconds after the pre-checkout query was sent.

---

### `answer_shipping_query(shipping_query_id, ok, shipping_options, error_message, request_timeout)`

If you sent an invoice requesting a shipping address and the parameter *is_flexible* was specified, the Bot API will send an :class:`aiogram.types.update.Update` with a *shipping_query* field to the bot. Use this method to reply to shipping queries. On success, :code:`True` is returned.

Source: https://core.telegram.org/bots/api#answershippingquery

Parameters:
    shipping_query_id (``str``):
        Unique identifier for the query to be answered

    ok (``bool``):
        Pass :code:`True` if delivery to the specified address is possible and :code:`False` if there are any problems (for example, if delivery to the specified address is not possible)

    shipping_options (``list[ShippingOption] | None``):
        Required if *ok* is :code:`True`. A JSON-serialized array of available shipping options.

    error_message (``str | None``):
        Required if *ok* is :code:`False`. Error message in human readable form that explains why it is impossible to complete the order (e.g. 'Sorry, delivery to your desired address is unavailable'). Telegram will display this message to the user.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: On success, :code:`True` is returned.

---

### `answer_web_app_query(web_app_query_id, result, request_timeout)`

Use this method to set the result of an interaction with a `Web App <https://core.telegram.org/bots/webapps>`_ and send a corresponding message on behalf of the user to the chat from which the query originated. On success, a :class:`aiogram.types.sent_web_app_message.SentWebAppMessage` object is returned.

Source: https://core.telegram.org/bots/api#answerwebappquery

Parameters:
    web_app_query_id (``str``):
        Unique identifier for the query to be answered

    result (``InlineQueryResultUnion``):
        A JSON-serialized object describing the message to be sent

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``SentWebAppMessage``: On success, a :class:`aiogram.types.sent_web_app_message.SentWebAppMessage` object is returned.

---

### `approve_chat_join_request(chat_id, user_id, request_timeout)`

Use this method to approve a chat join request. The bot must be an administrator in the chat for this to work and must have the *can_invite_users* administrator right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#approvechatjoinrequest

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `approve_suggested_post(chat_id, message_id, send_date, request_timeout)`

Use this method to approve a suggested post in a direct messages chat. The bot must have the 'can_post_messages' administrator right in the corresponding channel chat. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#approvesuggestedpost

Parameters:
    chat_id (``int``):
        Unique identifier for the target direct messages chat

    message_id (``int``):
        Identifier of a suggested post message to approve

    send_date (``DateTimeUnion | None``):
        Point in time (Unix timestamp) when the post is expected to be published; omit if the date has already been specified when the suggested post was created. If specified, then the date must be not more than 2678400 seconds (30 days) in the future

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `ban_chat_member(chat_id, user_id, until_date, revoke_messages, request_timeout)`

Use this method to ban a user in a group, a supergroup or a channel. In the case of supergroups and channels, the user will not be able to return to the chat on their own using invite links, etc., unless `unbanned <https://core.telegram.org/bots/api#unbanchatmember>`_ first. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#banchatmember

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target group or username of the target supergroup or channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    until_date (``DateTimeUnion | None``):
        Date when the user will be unbanned; Unix time. If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever. Applied for supergroups and channels only.

    revoke_messages (``bool | None``):
        Pass :code:`True` to delete all messages from the chat for the user that is being removed. If :code:`False`, the user will be able to see messages in the group that were sent before the user was removed. Always :code:`True` for supergroups and channels.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `ban_chat_sender_chat(chat_id, sender_chat_id, request_timeout)`

Use this method to ban a channel chat in a supergroup or a channel. Until the chat is `unbanned <https://core.telegram.org/bots/api#unbanchatsenderchat>`_, the owner of the banned chat won't be able to send messages on behalf of **any of their channels**. The bot must be an administrator in the supergroup or channel for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#banchatsenderchat

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    sender_chat_id (``int``):
        Unique identifier of the target sender chat

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `close(request_timeout)`

Use this method to close the bot instance before moving it from one local server to another. You need to delete the webhook before calling this method to ensure that the bot isn't launched again after server restart. The method will return error 429 in the first 10 minutes after the bot is launched. Returns :code:`True` on success. Requires no parameters.

Source: https://core.telegram.org/bots/api#close

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Requires no parameters.

---

### `close_forum_topic(chat_id, message_thread_id, request_timeout)`

Use this method to close an open topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights, unless it is the creator of the topic. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#closeforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    message_thread_id (``int``):
        Unique identifier for the target message thread of the forum topic

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `close_general_forum_topic(chat_id, request_timeout)`

Use this method to close an open 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#closegeneralforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `context(auto_close)`

Generate bot context

Parameters:
    auto_close (``bool``):
        close session on exit

---

### `convert_gift_to_stars(business_connection_id, owned_gift_id, request_timeout)`

Converts a given regular gift to Telegram Stars. Requires the *can_convert_gifts_to_stars* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#convertgifttostars

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    owned_gift_id (``str``):
        Unique identifier of the regular gift that should be converted to Telegram Stars

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `copy_message(chat_id, from_chat_id, message_id, message_thread_id, direct_messages_topic_id, video_start_timestamp, caption, parse_mode, caption_entities, show_caption_above_media, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to copy messages of any kind. Service messages, paid media messages, giveaway messages, giveaway winners messages, and invoice messages can't be copied. A quiz :class:`aiogram.methods.poll.Poll` can be copied only if the value of the field *correct_option_id* is known to the bot. The method is analogous to the method :class:`aiogram.methods.forward_message.ForwardMessage`, but the copied message doesn't have a link to the original message. Returns the :class:`aiogram.types.message_id.MessageId` of the sent message on success.

Source: https://core.telegram.org/bots/api#copymessage

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    from_chat_id (``ChatIdUnion``):
        Unique identifier for the chat where the original message was sent (or channel username in the format :code:`@channelusername`)

    message_id (``int``):
        Message identifier in the chat specified in *from_chat_id*

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    video_start_timestamp (``DateTimeUnion | None``):
        New start timestamp for the copied video in the message

    caption (``str | None``):
        New caption for media, 0-1024 characters after entities parsing. If not specified, the original caption is kept

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the new caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the new caption, which can be specified instead of *parse_mode*

    show_caption_above_media (``bool | Default | None``):
        Pass :code:`True`, if the caption must be shown above the message media. Ignored if a new caption isn't specified.

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; only available when copying to private chats

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``MessageId``: Returns the :class:`aiogram.types.message_id.MessageId` of the sent message on success.

---

### `copy_messages(chat_id, from_chat_id, message_ids, message_thread_id, direct_messages_topic_id, disable_notification, protect_content, remove_caption, request_timeout)`

Use this method to copy messages of any kind. If some of the specified messages can't be found or copied, they are skipped. Service messages, paid media messages, giveaway messages, giveaway winners messages, and invoice messages can't be copied. A quiz :class:`aiogram.methods.poll.Poll` can be copied only if the value of the field *correct_option_id* is known to the bot. The method is analogous to the method :class:`aiogram.methods.forward_messages.ForwardMessages`, but the copied messages don't have a link to the original message. Album grouping is kept for copied messages. On success, an array of :class:`aiogram.types.message_id.MessageId` of the sent messages is returned.

Source: https://core.telegram.org/bots/api#copymessages

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    from_chat_id (``ChatIdUnion``):
        Unique identifier for the chat where the original messages were sent (or channel username in the format :code:`@channelusername`)

    message_ids (``list[int]``):
        A JSON-serialized list of 1-100 identifiers of messages in the chat *from_chat_id* to copy. The identifiers must be specified in a strictly increasing order.

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the messages will be sent; required if the messages are sent to a direct messages chat

    disable_notification (``bool | None``):
        Sends the messages `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | None``):
        Protects the contents of the sent messages from forwarding and saving

    remove_caption (``bool | None``):
        Pass :code:`True` to copy the messages without their captions

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[MessageId]``: On success, an array of :class:`aiogram.types.message_id.MessageId` of the sent messages is returned.

---

### `create_chat_invite_link(chat_id, name, expire_date, member_limit, creates_join_request, request_timeout)`

Use this method to create an additional invite link for a chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. The link can be revoked using the method :class:`aiogram.methods.revoke_chat_invite_link.RevokeChatInviteLink`. Returns the new invite link as :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

Source: https://core.telegram.org/bots/api#createchatinvitelink

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    name (``str | None``):
        Invite link name; 0-32 characters

    expire_date (``DateTimeUnion | None``):
        Point in time (Unix timestamp) when the link will expire

    member_limit (``int | None``):
        The maximum number of users that can be members of the chat simultaneously after joining the chat via this invite link; 1-99999

    creates_join_request (``bool | None``):
        :code:`True`, if users joining the chat via the link need to be approved by chat administrators. If :code:`True`, *member_limit* can't be specified

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatInviteLink``: Returns the new invite link as :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

---

### `create_chat_subscription_invite_link(chat_id, subscription_period, subscription_price, name, request_timeout)`

Use this method to create a `subscription invite link <https://telegram.org/blog/superchannels-star-reactions-subscriptions#star-subscriptions>`_ for a channel chat. The bot must have the *can_invite_users* administrator rights. The link can be edited using the method :class:`aiogram.methods.edit_chat_subscription_invite_link.EditChatSubscriptionInviteLink` or revoked using the method :class:`aiogram.methods.revoke_chat_invite_link.RevokeChatInviteLink`. Returns the new invite link as a :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

Source: https://core.telegram.org/bots/api#createchatsubscriptioninvitelink

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target channel chat or username of the target channel (in the format :code:`@channelusername`)

    subscription_period (``DateTimeUnion``):
        The number of seconds the subscription will be active for before the next payment. Currently, it must always be 2592000 (30 days).

    subscription_price (``int``):
        The amount of Telegram Stars a user must pay initially and after each subsequent subscription period to be a member of the chat; 1-10000

    name (``str | None``):
        Invite link name; 0-32 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatInviteLink``: Returns the new invite link as a :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

---

### `create_forum_topic(chat_id, name, icon_color, icon_custom_emoji_id, request_timeout)`

Use this method to create a topic in a forum supergroup chat or a private chat with a user. In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator right. Returns information about the created topic as a :class:`aiogram.types.forum_topic.ForumTopic` object.

Source: https://core.telegram.org/bots/api#createforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    name (``str``):
        Topic name, 1-128 characters

    icon_color (``int | None``):
        Color of the topic icon in RGB format. Currently, must be one of 7322096 (0x6FB9F0), 16766590 (0xFFD67E), 13338331 (0xCB86DB), 9367192 (0x8EEE98), 16749490 (0xFF93B2), or 16478047 (0xFB6F5F)

    icon_custom_emoji_id (``str | None``):
        Unique identifier of the custom emoji shown as the topic icon. Use :class:`aiogram.methods.get_forum_topic_icon_stickers.GetForumTopicIconStickers` to get all allowed custom emoji identifiers.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ForumTopic``: Returns information about the created topic as a :class:`aiogram.types.forum_topic.ForumTopic` object.

---

### `create_invoice_link(title, description, payload, currency, prices, business_connection_id, provider_token, subscription_period, max_tip_amount, suggested_tip_amounts, provider_data, photo_url, photo_size, photo_width, photo_height, need_name, need_phone_number, need_email, need_shipping_address, send_phone_number_to_provider, send_email_to_provider, is_flexible, request_timeout)`

Use this method to create a link for an invoice. Returns the created invoice link as *String* on success.

Source: https://core.telegram.org/bots/api#createinvoicelink

Parameters:
    title (``str``):
        Product name, 1-32 characters

    description (``str``):
        Product description, 1-255 characters

    payload (``str``):
        Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use it for your internal processes.

    currency (``str``):
        Three-letter ISO 4217 currency code, see `more on currencies <https://core.telegram.org/bots/payments#supported-currencies>`_. Pass 'XTR' for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    prices (``list[LabeledPrice]``):
        Price breakdown, a JSON-serialized list of components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.). Must contain exactly one item for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the link will be created. For payments in `Telegram Stars <https://t.me/BotNews/90>`_ only.

    provider_token (``str | None``):
        Payment provider token, obtained via `@BotFather <https://t.me/botfather>`_. Pass an empty string for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    subscription_period (``int | None``):
        The number of seconds the subscription will be active for before the next payment. The currency must be set to 'XTR' (Telegram Stars) if the parameter is used. Currently, it must always be 2592000 (30 days) if specified. Any number of subscriptions can be active for a given bot at the same time, including multiple concurrent subscriptions from the same user. Subscription price must no exceed 10000 Telegram Stars.

    max_tip_amount (``int | None``):
        The maximum accepted amount for tips in the *smallest units* of the currency (integer, **not** float/double). For example, for a maximum tip of :code:`US$ 1.45` pass :code:`max_tip_amount = 145`. See the *exp* parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies). Defaults to 0. Not supported for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    suggested_tip_amounts (``list[int] | None``):
        A JSON-serialized array of suggested amounts of tips in the *smallest units* of the currency (integer, **not** float/double). At most 4 suggested tip amounts can be specified. The suggested tip amounts must be positive, passed in a strictly increased order and must not exceed *max_tip_amount*.

    provider_data (``str | None``):
        JSON-serialized data about the invoice, which will be shared with the payment provider. A detailed description of required fields should be provided by the payment provider.

    photo_url (``str | None``):
        URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service.

    photo_size (``int | None``):
        Photo size in bytes

    photo_width (``int | None``):
        Photo width

    photo_height (``int | None``):
        Photo height

    need_name (``bool | None``):
        Pass :code:`True` if you require the user's full name to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    need_phone_number (``bool | None``):
        Pass :code:`True` if you require the user's phone number to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    need_email (``bool | None``):
        Pass :code:`True` if you require the user's email address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    need_shipping_address (``bool | None``):
        Pass :code:`True` if you require the user's shipping address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    send_phone_number_to_provider (``bool | None``):
        Pass :code:`True` if the user's phone number should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    send_email_to_provider (``bool | None``):
        Pass :code:`True` if the user's email address should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    is_flexible (``bool | None``):
        Pass :code:`True` if the final price depends on the shipping method. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``str``: Returns the created invoice link as *String* on success.

---

### `create_new_sticker_set(user_id, name, title, stickers, sticker_type, needs_repainting, sticker_format, request_timeout)`

Use this method to create a new sticker set owned by a user. The bot will be able to edit the sticker set thus created. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#createnewstickerset

Parameters:
    user_id (``int``):
        User identifier of created sticker set owner

    name (``str``):
        Short name of sticker set, to be used in :code:`t.me/addstickers/` URLs (e.g., *animals*). Can contain only English letters, digits and underscores. Must begin with a letter, can't contain consecutive underscores and must end in :code:`"_by_<bot_username>"`. :code:`<bot_username>` is case insensitive. 1-64 characters.

    title (``str``):
        Sticker set title, 1-64 characters

    stickers (``list[InputSticker]``):
        A JSON-serialized list of 1-50 initial stickers to be added to the sticker set

    sticker_type (``str | None``):
        Type of stickers in the set, pass 'regular', 'mask', or 'custom_emoji'. By default, a regular sticker set is created.

    needs_repainting (``bool | None``):
        Pass :code:`True` if stickers in the sticker set must be repainted to the color of text when used in messages, the accent color if used as emoji status, white on chat photos, or another appropriate color based on context; for custom emoji sticker sets only

    sticker_format (``str | None``):
        Format of stickers in the set, must be one of 'static', 'animated', 'video'

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `decline_chat_join_request(chat_id, user_id, request_timeout)`

Use this method to decline a chat join request. The bot must be an administrator in the chat for this to work and must have the *can_invite_users* administrator right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#declinechatjoinrequest

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `decline_suggested_post(chat_id, message_id, comment, request_timeout)`

Use this method to decline a suggested post in a direct messages chat. The bot must have the 'can_manage_direct_messages' administrator right in the corresponding channel chat. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#declinesuggestedpost

Parameters:
    chat_id (``int``):
        Unique identifier for the target direct messages chat

    message_id (``int``):
        Identifier of a suggested post message to decline

    comment (``str | None``):
        Comment for the creator of the suggested post; 0-128 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_business_messages(business_connection_id, message_ids, request_timeout)`

Delete messages on behalf of a business account. Requires the *can_delete_sent_messages* business bot right to delete messages sent by the bot itself, or the *can_delete_all_messages* business bot right to delete any message. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletebusinessmessages

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection on behalf of which to delete the messages

    message_ids (``list[int]``):
        A JSON-serialized list of 1-100 identifiers of messages to delete. All messages must be from the same chat. See :class:`aiogram.methods.delete_message.DeleteMessage` for limitations on which messages can be deleted

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_chat_photo(chat_id, request_timeout)`

Use this method to delete a chat photo. Photos can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletechatphoto

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_chat_sticker_set(chat_id, request_timeout)`

Use this method to delete a group sticker set from a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Use the field *can_set_sticker_set* optionally returned in :class:`aiogram.methods.get_chat.GetChat` requests to check if the bot can use this method. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletechatstickerset

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_forum_topic(chat_id, message_thread_id, request_timeout)`

Use this method to delete a forum topic along with all its messages in a forum supergroup chat or a private chat with a user. In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the *can_delete_messages* administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deleteforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    message_thread_id (``int``):
        Unique identifier for the target message thread of the forum topic

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_message(chat_id, message_id, request_timeout)`

Use this method to delete a message, including service messages, with the following limitations:

- A message can only be deleted if it was sent less than 48 hours ago.

- Service messages about a supergroup, channel, or forum topic creation can't be deleted.

- A dice message in a private chat can only be deleted if it was sent more than 24 hours ago.

- Bots can delete outgoing messages in private chats, groups, and supergroups.

- Bots can delete incoming messages in private chats.

- Bots granted *can_post_messages* permissions can delete outgoing messages in channels.

- If the bot is an administrator of a group, it can delete any message there.

- If the bot has *can_delete_messages* administrator right in a supergroup or a channel, it can delete any message there.

- If the bot has *can_manage_direct_messages* administrator right in a channel, it can delete any message in the corresponding direct messages chat.

Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletemessage

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int``):
        Identifier of the message to delete

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Use this method to delete a message, including service messages, with the following limitations:

---

### `delete_messages(chat_id, message_ids, request_timeout)`

Use this method to delete multiple messages simultaneously. If some of the specified messages can't be found, they are skipped. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletemessages

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_ids (``list[int]``):
        A JSON-serialized list of 1-100 identifiers of messages to delete. See :class:`aiogram.methods.delete_message.DeleteMessage` for limitations on which messages can be deleted

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_my_commands(scope, language_code, request_timeout)`

Use this method to delete the list of the bot's commands for the given scope and user language. After deletion, `higher level commands <https://core.telegram.org/bots/api#determining-list-of-commands>`_ will be shown to affected users. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletemycommands

Parameters:
    scope (``BotCommandScopeUnion | None``):
        A JSON-serialized object, describing scope of users for which the commands are relevant. Defaults to :class:`aiogram.types.bot_command_scope_default.BotCommandScopeDefault`.

    language_code (``str | None``):
        A two-letter ISO 639-1 language code. If empty, commands will be applied to all users from the given scope, for whose language there are no dedicated commands

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_sticker_from_set(sticker, request_timeout)`

Use this method to delete a sticker from a set created by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletestickerfromset

Parameters:
    sticker (``str``):
        File identifier of the sticker

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_sticker_set(name, request_timeout)`

Use this method to delete a sticker set that was created by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletestickerset

Parameters:
    name (``str``):
        Sticker set name

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_story(business_connection_id, story_id, request_timeout)`

Deletes a story previously posted by the bot on behalf of a managed business account. Requires the *can_manage_stories* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletestory

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    story_id (``int``):
        Unique identifier of the story to delete

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `delete_webhook(drop_pending_updates, request_timeout)`

Use this method to remove webhook integration if you decide to switch back to :class:`aiogram.methods.get_updates.GetUpdates`. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#deletewebhook

Parameters:
    drop_pending_updates (``bool | None``):
        Pass :code:`True` to drop all pending updates

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `download(file, destination, timeout, chunk_size, seek)`

Download file by file_id or Downloadable object to destination.

If you want to automatically create destination (:class:`io.BytesIO`) use default
value of destination and handle result of this method.

Parameters:
    file (``str | Downloadable``):
        file_id or Downloadable object

    destination (``BinaryIO | pathlib.Path | str | None``):
        Filename, file path or instance of :class:`io.IOBase`. For e.g. :class:`io.BytesIO`, defaults to None

    timeout (``int``):
        Total timeout in seconds, defaults to 30

    chunk_size (``int``):
        File chunks size, defaults to 64 kb

    seek (``bool``):
        Go to start of file when downloading is finished. Used only for destination with :class:`typing.BinaryIO` type, defaults to True

---

### `download_file(file_path, destination, timeout, chunk_size, seek)`

Download file by file_path to destination.

If you want to automatically create destination (:class:`io.BytesIO`) use default
value of destination and handle result of this method.

Parameters:
    file_path (``str | pathlib.Path``):
        File path on Telegram server (You can get it from :obj:`aiogram.types.File`)

    destination (``BinaryIO | pathlib.Path | str | None``):
        Filename, file path or instance of :class:`io.IOBase`. For e.g. :class:`io.BytesIO`, defaults to None

    timeout (``int``):
        Total timeout in seconds, defaults to 30

    chunk_size (``int``):
        File chunks size, defaults to 64 kb

    seek (``bool``):
        Go to start of file when downloading is finished. Used only for destination with :class:`typing.BinaryIO` type, defaults to True

---

### `edit_chat_invite_link(chat_id, invite_link, name, expire_date, member_limit, creates_join_request, request_timeout)`

Use this method to edit a non-primary invite link created by the bot. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns the edited invite link as a :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

Source: https://core.telegram.org/bots/api#editchatinvitelink

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    invite_link (``str``):
        The invite link to edit

    name (``str | None``):
        Invite link name; 0-32 characters

    expire_date (``DateTimeUnion | None``):
        Point in time (Unix timestamp) when the link will expire

    member_limit (``int | None``):
        The maximum number of users that can be members of the chat simultaneously after joining the chat via this invite link; 1-99999

    creates_join_request (``bool | None``):
        :code:`True`, if users joining the chat via the link need to be approved by chat administrators. If :code:`True`, *member_limit* can't be specified

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatInviteLink``: Returns the edited invite link as a :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

---

### `edit_chat_subscription_invite_link(chat_id, invite_link, name, request_timeout)`

Use this method to edit a subscription invite link created by the bot. The bot must have the *can_invite_users* administrator rights. Returns the edited invite link as a :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

Source: https://core.telegram.org/bots/api#editchatsubscriptioninvitelink

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    invite_link (``str``):
        The invite link to edit

    name (``str | None``):
        Invite link name; 0-32 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatInviteLink``: Returns the edited invite link as a :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

---

### `edit_forum_topic(chat_id, message_thread_id, name, icon_custom_emoji_id, request_timeout)`

Use this method to edit name and icon of a topic in a forum supergroup chat or a private chat with a user. In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights, unless it is the creator of the topic. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#editforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    message_thread_id (``int``):
        Unique identifier for the target message thread of the forum topic

    name (``str | None``):
        New topic name, 0-128 characters. If not specified or empty, the current name of the topic will be kept

    icon_custom_emoji_id (``str | None``):
        New unique identifier of the custom emoji shown as the topic icon. Use :class:`aiogram.methods.get_forum_topic_icon_stickers.GetForumTopicIconStickers` to get all allowed custom emoji identifiers. Pass an empty string to remove the icon. If not specified, the current icon will be kept

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `edit_general_forum_topic(chat_id, name, request_timeout)`

Use this method to edit the name of the 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#editgeneralforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    name (``str``):
        New topic name, 1-128 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `edit_message_caption(business_connection_id, chat_id, message_id, inline_message_id, caption, parse_mode, caption_entities, show_caption_above_media, reply_markup, request_timeout)`

Use this method to edit captions of messages. On success, if the edited message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned. Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

Source: https://core.telegram.org/bots/api#editmessagecaption

Parameters:
    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    chat_id (``ChatIdUnion | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the message to edit

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    caption (``str | None``):
        New caption of the message, 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the message caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    show_caption_above_media (``bool | Default | None``):
        Pass :code:`True`, if the caption must be shown above the message media. Supported only for animation, photo and video messages.

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

---

### `edit_message_checklist(business_connection_id, chat_id, message_id, checklist, reply_markup, request_timeout)`

Use this method to edit a checklist on behalf of a connected business account. On success, the edited :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#editmessagechecklist

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection on behalf of which the message will be sent

    chat_id (``int``):
        Unique identifier for the target chat

    message_id (``int``):
        Unique identifier for the target message

    checklist (``InputChecklist``):
        A JSON-serialized object for the new checklist

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for the new `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_ for the message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the edited :class:`aiogram.types.message.Message` is returned.

---

### `edit_message_live_location(latitude, longitude, business_connection_id, chat_id, message_id, inline_message_id, live_period, horizontal_accuracy, heading, proximity_alert_radius, reply_markup, request_timeout)`

Use this method to edit live location messages. A location can be edited until its *live_period* expires or editing is explicitly disabled by a call to :class:`aiogram.methods.stop_message_live_location.StopMessageLiveLocation`. On success, if the edited message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned.

Source: https://core.telegram.org/bots/api#editmessagelivelocation

Parameters:
    latitude (``float``):
        Latitude of new location

    longitude (``float``):
        Longitude of new location

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    chat_id (``ChatIdUnion | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the message to edit

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    live_period (``int | None``):
        New period in seconds during which the location can be updated, starting from the message send date. If 0x7FFFFFFF is specified, then the location can be updated forever. Otherwise, the new value must not exceed the current *live_period* by more than a day, and the live location expiration date must remain within the next 90 days. If not specified, then *live_period* remains unchanged

    horizontal_accuracy (``float | None``):
        The radius of uncertainty for the location, measured in meters; 0-1500

    heading (``int | None``):
        Direction in which the user is moving, in degrees. Must be between 1 and 360 if specified.

    proximity_alert_radius (``int | None``):
        The maximum distance for proximity alerts about approaching another chat member, in meters. Must be between 1 and 100000 if specified.

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for a new `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: On success, if the edited message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned.

---

### `edit_message_media(media, business_connection_id, chat_id, message_id, inline_message_id, reply_markup, request_timeout)`

Use this method to edit animation, audio, document, photo, or video messages, or to add media to text messages. If a message is part of a message album, then it can be edited only to an audio for audio albums, only to a document for document albums and to a photo or a video otherwise. When an inline message is edited, a new file can't be uploaded; use a previously uploaded file via its file_id or specify a URL. On success, if the edited message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned. Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

Source: https://core.telegram.org/bots/api#editmessagemedia

Parameters:
    media (``InputMediaUnion``):
        A JSON-serialized object for a new media content of the message

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    chat_id (``ChatIdUnion | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the message to edit

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for a new `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

---

### `edit_message_reply_markup(business_connection_id, chat_id, message_id, inline_message_id, reply_markup, request_timeout)`

Use this method to edit only the reply markup of messages. On success, if the edited message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned. Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

Source: https://core.telegram.org/bots/api#editmessagereplymarkup

Parameters:
    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    chat_id (``ChatIdUnion | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the message to edit

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

---

### `edit_message_text(text, business_connection_id, chat_id, message_id, inline_message_id, parse_mode, entities, link_preview_options, reply_markup, disable_web_page_preview, request_timeout)`

Use this method to edit text and `game <https://core.telegram.org/bots/api#games>`_ messages. On success, if the edited message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned. Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

Source: https://core.telegram.org/bots/api#editmessagetext

Parameters:
    text (``str``):
        New text of the message, 1-4096 characters after entities parsing

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    chat_id (``ChatIdUnion | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the message to edit

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the message text. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in message text, which can be specified instead of *parse_mode*

    link_preview_options (``LinkPreviewOptions | Default | None``):
        Link preview generation options for the message

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    disable_web_page_preview (``bool | Default | None``):
        Disables link previews for links in this message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: Note that business messages that were not sent by the bot and do not contain an inline keyboard can only be edited within **48 hours** from the time they were sent.

---

### `edit_story(business_connection_id, story_id, content, caption, parse_mode, caption_entities, areas, request_timeout)`

Edits a story previously posted by the bot on behalf of a managed business account. Requires the *can_manage_stories* business bot right. Returns :class:`aiogram.types.story.Story` on success.

Source: https://core.telegram.org/bots/api#editstory

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    story_id (``int``):
        Unique identifier of the story to edit

    content (``InputStoryContentUnion``):
        Content of the story

    caption (``str | None``):
        Caption of the story, 0-2048 characters after entities parsing

    parse_mode (``str | None``):
        Mode for parsing entities in the story caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    areas (``list[StoryArea] | None``):
        A JSON-serialized list of clickable areas to be shown on the story

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Story``: Returns :class:`aiogram.types.story.Story` on success.

---

### `edit_user_star_subscription(user_id, telegram_payment_charge_id, is_canceled, request_timeout)`

Allows the bot to cancel or re-enable extension of a subscription paid in Telegram Stars. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#edituserstarsubscription

Parameters:
    user_id (``int``):
        Identifier of the user whose subscription will be edited

    telegram_payment_charge_id (``str``):
        Telegram payment identifier for the subscription

    is_canceled (``bool``):
        Pass :code:`True` to cancel extension of the user subscription; the subscription must be active up to the end of the current subscription period. Pass :code:`False` to allow the user to re-enable a subscription that was previously canceled by the bot.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `export_chat_invite_link(chat_id, request_timeout)`

Use this method to generate a new primary invite link for a chat; any previously generated primary link is revoked. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns the new invite link as *String* on success.

 Note: Each administrator in a chat generates their own invite links. Bots can't use invite links generated by other administrators. If you want your bot to work with invite links, it will need to generate its own link using :class:`aiogram.methods.export_chat_invite_link.ExportChatInviteLink` or by calling the :class:`aiogram.methods.get_chat.GetChat` method. If your bot needs to generate a new primary invite link replacing its previous one, use :class:`aiogram.methods.export_chat_invite_link.ExportChatInviteLink` again.

Source: https://core.telegram.org/bots/api#exportchatinvitelink

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``str``: If your bot needs to generate a new primary invite link replacing its previous one, use :class:`aiogram.methods.export_chat_invite_link.ExportChatInviteLink` again.

---

### `forward_message(chat_id, from_chat_id, message_id, message_thread_id, direct_messages_topic_id, video_start_timestamp, disable_notification, protect_content, message_effect_id, suggested_post_parameters, request_timeout)`

Use this method to forward messages of any kind. Service messages and messages with protected content can't be forwarded. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#forwardmessage

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    from_chat_id (``ChatIdUnion``):
        Unique identifier for the chat where the original message was sent (or channel username in the format :code:`@channelusername`)

    message_id (``int``):
        Message identifier in the chat specified in *from_chat_id*

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be forwarded; required if the message is forwarded to a direct messages chat

    video_start_timestamp (``DateTimeUnion | None``):
        New start timestamp for the forwarded video in the message

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the forwarded message from forwarding and saving

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; only available when forwarding to private chats

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `forward_messages(chat_id, from_chat_id, message_ids, message_thread_id, direct_messages_topic_id, disable_notification, protect_content, request_timeout)`

Use this method to forward multiple messages of any kind. If some of the specified messages can't be found or forwarded, they are skipped. Service messages and messages with protected content can't be forwarded. Album grouping is kept for forwarded messages. On success, an array of :class:`aiogram.types.message_id.MessageId` of the sent messages is returned.

Source: https://core.telegram.org/bots/api#forwardmessages

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    from_chat_id (``ChatIdUnion``):
        Unique identifier for the chat where the original messages were sent (or channel username in the format :code:`@channelusername`)

    message_ids (``list[int]``):
        A JSON-serialized list of 1-100 identifiers of messages in the chat *from_chat_id* to forward. The identifiers must be specified in a strictly increasing order.

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the messages will be forwarded; required if the messages are forwarded to a direct messages chat

    disable_notification (``bool | None``):
        Sends the messages `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | None``):
        Protects the contents of the forwarded messages from forwarding and saving

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[MessageId]``: On success, an array of :class:`aiogram.types.message_id.MessageId` of the sent messages is returned.

---

### `get_available_gifts(request_timeout)`

Returns the list of gifts that can be sent by the bot to users and channel chats. Requires no parameters. Returns a :class:`aiogram.types.gifts.Gifts` object.

Source: https://core.telegram.org/bots/api#getavailablegifts

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Gifts``: Returns a :class:`aiogram.types.gifts.Gifts` object.

---

### `get_business_account_gifts(business_connection_id, exclude_unsaved, exclude_saved, exclude_unlimited, exclude_limited_upgradable, exclude_limited_non_upgradable, exclude_unique, exclude_from_blockchain, sort_by_price, offset, limit, exclude_limited, request_timeout)`

Returns the gifts received and owned by a managed business account. Requires the *can_view_gifts_and_stars* business bot right. Returns :class:`aiogram.types.owned_gifts.OwnedGifts` on success.

Source: https://core.telegram.org/bots/api#getbusinessaccountgifts

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    exclude_unsaved (``bool | None``):
        Pass :code:`True` to exclude gifts that aren't saved to the account's profile page

    exclude_saved (``bool | None``):
        Pass :code:`True` to exclude gifts that are saved to the account's profile page

    exclude_unlimited (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased an unlimited number of times

    exclude_limited_upgradable (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times and can be upgraded to unique

    exclude_limited_non_upgradable (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times and can't be upgraded to unique

    exclude_unique (``bool | None``):
        Pass :code:`True` to exclude unique gifts

    exclude_from_blockchain (``bool | None``):
        Pass :code:`True` to exclude gifts that were assigned from the TON blockchain and can't be resold or transferred in Telegram

    sort_by_price (``bool | None``):
        Pass :code:`True` to sort results by gift price instead of send date. Sorting is applied before pagination.

    offset (``str | None``):
        Offset of the first entry to return as received from the previous request; use empty string to get the first chunk of results

    limit (``int | None``):
        The maximum number of gifts to be returned; 1-100. Defaults to 100

    exclude_limited (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``OwnedGifts``: Returns :class:`aiogram.types.owned_gifts.OwnedGifts` on success.

---

### `get_business_account_star_balance(business_connection_id, request_timeout)`

Returns the amount of Telegram Stars owned by a managed business account. Requires the *can_view_gifts_and_stars* business bot right. Returns :class:`aiogram.types.star_amount.StarAmount` on success.

Source: https://core.telegram.org/bots/api#getbusinessaccountstarbalance

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``StarAmount``: Returns :class:`aiogram.types.star_amount.StarAmount` on success.

---

### `get_business_connection(business_connection_id, request_timeout)`

Use this method to get information about the connection of the bot with a business account. Returns a :class:`aiogram.types.business_connection.BusinessConnection` object on success.

Source: https://core.telegram.org/bots/api#getbusinessconnection

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``BusinessConnection``: Returns a :class:`aiogram.types.business_connection.BusinessConnection` object on success.

---

### `get_chat(chat_id, request_timeout)`

Use this method to get up-to-date information about the chat. Returns a :class:`aiogram.types.chat_full_info.ChatFullInfo` object on success.

Source: https://core.telegram.org/bots/api#getchat

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup or channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatFullInfo``: Returns a :class:`aiogram.types.chat_full_info.ChatFullInfo` object on success.

---

### `get_chat_administrators(chat_id, request_timeout)`

Use this method to get a list of administrators in a chat, which aren't bots. Returns an Array of :class:`aiogram.types.chat_member.ChatMember` objects.

Source: https://core.telegram.org/bots/api#getchatadministrators

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup or channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[ResultChatMemberUnion]``: Returns an Array of :class:`aiogram.types.chat_member.ChatMember` objects.

---

### `get_chat_gifts(chat_id, exclude_unsaved, exclude_saved, exclude_unlimited, exclude_limited_upgradable, exclude_limited_non_upgradable, exclude_from_blockchain, exclude_unique, sort_by_price, offset, limit, request_timeout)`

Returns the gifts owned by a chat. Returns :class:`aiogram.types.owned_gifts.OwnedGifts` on success.

Source: https://core.telegram.org/bots/api#getchatgifts

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    exclude_unsaved (``bool | None``):
        Pass :code:`True` to exclude gifts that aren't saved to the chat's profile page. Always :code:`True`, unless the bot has the *can_post_messages* administrator right in the channel.

    exclude_saved (``bool | None``):
        Pass :code:`True` to exclude gifts that are saved to the chat's profile page. Always :code:`False`, unless the bot has the *can_post_messages* administrator right in the channel.

    exclude_unlimited (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased an unlimited number of times

    exclude_limited_upgradable (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times and can be upgraded to unique

    exclude_limited_non_upgradable (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times and can't be upgraded to unique

    exclude_from_blockchain (``bool | None``):
        Pass :code:`True` to exclude gifts that were assigned from the TON blockchain and can't be resold or transferred in Telegram

    exclude_unique (``bool | None``):
        Pass :code:`True` to exclude unique gifts

    sort_by_price (``bool | None``):
        Pass :code:`True` to sort results by gift price instead of send date. Sorting is applied before pagination.

    offset (``str | None``):
        Offset of the first entry to return as received from the previous request; use an empty string to get the first chunk of results

    limit (``int | None``):
        The maximum number of gifts to be returned; 1-100. Defaults to 100

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``OwnedGifts``: Returns :class:`aiogram.types.owned_gifts.OwnedGifts` on success.

---

### `get_chat_member(chat_id, user_id, request_timeout)`

Use this method to get information about a member of a chat. The method is only guaranteed to work for other users if the bot is an administrator in the chat. Returns a :class:`aiogram.types.chat_member.ChatMember` object on success.

Source: https://core.telegram.org/bots/api#getchatmember

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup or channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ResultChatMemberUnion``: Returns a :class:`aiogram.types.chat_member.ChatMember` object on success.

---

### `get_chat_member_count(chat_id, request_timeout)`

Use this method to get the number of members in a chat. Returns *Int* on success.

Source: https://core.telegram.org/bots/api#getchatmembercount

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup or channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``int``: Returns *Int* on success.

---

### `get_chat_menu_button(chat_id, request_timeout)`

Use this method to get the current value of the bot's menu button in a private chat, or the default menu button. Returns :class:`aiogram.types.menu_button.MenuButton` on success.

Source: https://core.telegram.org/bots/api#getchatmenubutton

Parameters:
    chat_id (``int | None``):
        Unique identifier for the target private chat. If not specified, default bot's menu button will be returned

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ResultMenuButtonUnion``: Returns :class:`aiogram.types.menu_button.MenuButton` on success.

---

### `get_custom_emoji_stickers(custom_emoji_ids, request_timeout)`

Use this method to get information about custom emoji stickers by their identifiers. Returns an Array of :class:`aiogram.types.sticker.Sticker` objects.

Source: https://core.telegram.org/bots/api#getcustomemojistickers

Parameters:
    custom_emoji_ids (``list[str]``):
        A JSON-serialized list of custom emoji identifiers. At most 200 custom emoji identifiers can be specified.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[Sticker]``: Returns an Array of :class:`aiogram.types.sticker.Sticker` objects.

---

### `get_file(file_id, request_timeout)`

Use this method to get basic information about a file and prepare it for downloading. For the moment, bots can download files of up to 20MB in size. On success, a :class:`aiogram.types.file.File` object is returned. The file can then be downloaded via the link :code:`https://api.telegram.org/file/bot<token>/<file_path>`, where :code:`<file_path>` is taken from the response. It is guaranteed that the link will be valid for at least 1 hour. When the link expires, a new one can be requested by calling :class:`aiogram.methods.get_file.GetFile` again.
**Note:** This function may not preserve the original file name and MIME type. You should save the file's MIME type and name (if available) when the File object is received.

Source: https://core.telegram.org/bots/api#getfile

Parameters:
    file_id (``str``):
        File identifier to get information about

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``File``: You should save the file's MIME type and name (if available) when the File object is received.

---

### `get_forum_topic_icon_stickers(request_timeout)`

Use this method to get custom emoji stickers, which can be used as a forum topic icon by any user. Requires no parameters. Returns an Array of :class:`aiogram.types.sticker.Sticker` objects.

Source: https://core.telegram.org/bots/api#getforumtopiciconstickers

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[Sticker]``: Returns an Array of :class:`aiogram.types.sticker.Sticker` objects.

---

### `get_game_high_scores(user_id, chat_id, message_id, inline_message_id, request_timeout)`

Use this method to get data for high score tables. Will return the score of the specified user and several of their neighbors in a game. Returns an Array of :class:`aiogram.types.game_high_score.GameHighScore` objects.

 This method will currently return scores for the target user, plus two of their closest neighbors on each side. Will also return the top three users if the user and their neighbors are not among them. Please note that this behavior is subject to change.

Source: https://core.telegram.org/bots/api#getgamehighscores

Parameters:
    user_id (``int``):
        Target user id

    chat_id (``int | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the sent message

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[GameHighScore]``: Please note that this behavior is subject to change.

---

### `get_managed_bot_token(user_id, request_timeout)`

Use this method to get the token of a managed bot. Returns the token as *String* on success.

Source: https://core.telegram.org/bots/api#getmanagedbottoken

Parameters:
    user_id (``int``):
        User identifier of the managed bot whose token will be returned

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``str``: Returns the token as *String* on success.

---

### `get_me(request_timeout)`

A simple method for testing your bot's authentication token. Requires no parameters. Returns basic information about the bot in form of a :class:`aiogram.types.user.User` object.

Source: https://core.telegram.org/bots/api#getme

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``User``: Returns basic information about the bot in form of a :class:`aiogram.types.user.User` object.

---

### `get_my_commands(scope, language_code, request_timeout)`

Use this method to get the current list of the bot's commands for the given scope and user language. Returns an Array of :class:`aiogram.types.bot_command.BotCommand` objects. If commands aren't set, an empty list is returned.

Source: https://core.telegram.org/bots/api#getmycommands

Parameters:
    scope (``BotCommandScopeUnion | None``):
        A JSON-serialized object, describing scope of users. Defaults to :class:`aiogram.types.bot_command_scope_default.BotCommandScopeDefault`.

    language_code (``str | None``):
        A two-letter ISO 639-1 language code or an empty string

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[BotCommand]``: If commands aren't set, an empty list is returned.

---

### `get_my_default_administrator_rights(for_channels, request_timeout)`

Use this method to get the current default administrator rights of the bot. Returns :class:`aiogram.types.chat_administrator_rights.ChatAdministratorRights` on success.

Source: https://core.telegram.org/bots/api#getmydefaultadministratorrights

Parameters:
    for_channels (``bool | None``):
        Pass :code:`True` to get default administrator rights of the bot in channels. Otherwise, default administrator rights of the bot for groups and supergroups will be returned.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatAdministratorRights``: Returns :class:`aiogram.types.chat_administrator_rights.ChatAdministratorRights` on success.

---

### `get_my_description(language_code, request_timeout)`

Use this method to get the current bot description for the given user language. Returns :class:`aiogram.types.bot_description.BotDescription` on success.

Source: https://core.telegram.org/bots/api#getmydescription

Parameters:
    language_code (``str | None``):
        A two-letter ISO 639-1 language code or an empty string

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``BotDescription``: Returns :class:`aiogram.types.bot_description.BotDescription` on success.

---

### `get_my_name(language_code, request_timeout)`

Use this method to get the current bot name for the given user language. Returns :class:`aiogram.types.bot_name.BotName` on success.

Source: https://core.telegram.org/bots/api#getmyname

Parameters:
    language_code (``str | None``):
        A two-letter ISO 639-1 language code or an empty string

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``BotName``: Returns :class:`aiogram.types.bot_name.BotName` on success.

---

### `get_my_short_description(language_code, request_timeout)`

Use this method to get the current bot short description for the given user language. Returns :class:`aiogram.types.bot_short_description.BotShortDescription` on success.

Source: https://core.telegram.org/bots/api#getmyshortdescription

Parameters:
    language_code (``str | None``):
        A two-letter ISO 639-1 language code or an empty string

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``BotShortDescription``: Returns :class:`aiogram.types.bot_short_description.BotShortDescription` on success.

---

### `get_my_star_balance(request_timeout)`

A method to get the current Telegram Stars balance of the bot. Requires no parameters. On success, returns a :class:`aiogram.types.star_amount.StarAmount` object.

Source: https://core.telegram.org/bots/api#getmystarbalance

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``StarAmount``: On success, returns a :class:`aiogram.types.star_amount.StarAmount` object.

---

### `get_star_transactions(offset, limit, request_timeout)`

Returns the bot's Telegram Star transactions in chronological order. On success, returns a :class:`aiogram.types.star_transactions.StarTransactions` object.

Source: https://core.telegram.org/bots/api#getstartransactions

Parameters:
    offset (``int | None``):
        Number of transactions to skip in the response

    limit (``int | None``):
        The maximum number of transactions to be retrieved. Values between 1-100 are accepted. Defaults to 100.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``StarTransactions``: On success, returns a :class:`aiogram.types.star_transactions.StarTransactions` object.

---

### `get_sticker_set(name, request_timeout)`

Use this method to get a sticker set. On success, a :class:`aiogram.types.sticker_set.StickerSet` object is returned.

Source: https://core.telegram.org/bots/api#getstickerset

Parameters:
    name (``str``):
        Name of the sticker set

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``StickerSet``: On success, a :class:`aiogram.types.sticker_set.StickerSet` object is returned.

---

### `get_updates(offset, limit, timeout, allowed_updates, request_timeout)`

Use this method to receive incoming updates using long polling (`wiki <https://en.wikipedia.org/wiki/Push_technology#Long_polling>`_). Returns an Array of :class:`aiogram.types.update.Update` objects.

 **Notes**

 **1.** This method will not work if an outgoing webhook is set up.

 **2.** In order to avoid getting duplicate updates, recalculate *offset* after each server response.

Source: https://core.telegram.org/bots/api#getupdates

Parameters:
    offset (``int | None``):
        Identifier of the first update to be returned. Must be greater by one than the highest among the identifiers of previously received updates. By default, updates starting with the earliest unconfirmed update are returned. An update is considered confirmed as soon as :class:`aiogram.methods.get_updates.GetUpdates` is called with an *offset* higher than its *update_id*. The negative offset can be specified to retrieve updates starting from *-offset* update from the end of the updates queue. All previous updates will be forgotten.

    limit (``int | None``):
        Limits the number of updates to be retrieved. Values between 1-100 are accepted. Defaults to 100.

    timeout (``int | None``):
        Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling. Should be positive, short polling should be used for testing purposes only.

    allowed_updates (``list[str] | None``):
        A JSON-serialized list of the update types you want your bot to receive. For example, specify :code:`["message", "edited_channel_post", "callback_query"]` to only receive updates of these types. See :class:`aiogram.types.update.Update` for a complete list of available update types. Specify an empty list to receive all update types except *chat_member*, *message_reaction*, and *message_reaction_count* (default). If not specified, the previous setting will be used.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[Update]``: Returns an Array of :class:`aiogram.types.update.Update` objects.

---

### `get_user_chat_boosts(chat_id, user_id, request_timeout)`

Use this method to get the list of boosts added to a chat by a user. Requires administrator rights in the chat. Returns a :class:`aiogram.types.user_chat_boosts.UserChatBoosts` object.

Source: https://core.telegram.org/bots/api#getuserchatboosts

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the chat or username of the channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``UserChatBoosts``: Returns a :class:`aiogram.types.user_chat_boosts.UserChatBoosts` object.

---

### `get_user_gifts(user_id, exclude_unlimited, exclude_limited_upgradable, exclude_limited_non_upgradable, exclude_from_blockchain, exclude_unique, sort_by_price, offset, limit, request_timeout)`

Returns the gifts owned and hosted by a user. Returns :class:`aiogram.types.owned_gifts.OwnedGifts` on success.

Source: https://core.telegram.org/bots/api#getusergifts

Parameters:
    user_id (``int``):
        Unique identifier of the user

    exclude_unlimited (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased an unlimited number of times

    exclude_limited_upgradable (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times and can be upgraded to unique

    exclude_limited_non_upgradable (``bool | None``):
        Pass :code:`True` to exclude gifts that can be purchased a limited number of times and can't be upgraded to unique

    exclude_from_blockchain (``bool | None``):
        Pass :code:`True` to exclude gifts that were assigned from the TON blockchain and can't be resold or transferred in Telegram

    exclude_unique (``bool | None``):
        Pass :code:`True` to exclude unique gifts

    sort_by_price (``bool | None``):
        Pass :code:`True` to sort results by gift price instead of send date. Sorting is applied before pagination.

    offset (``str | None``):
        Offset of the first entry to return as received from the previous request; use an empty string to get the first chunk of results

    limit (``int | None``):
        The maximum number of gifts to be returned; 1-100. Defaults to 100

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``OwnedGifts``: Returns :class:`aiogram.types.owned_gifts.OwnedGifts` on success.

---

### `get_user_profile_audios(user_id, offset, limit, request_timeout)`

Use this method to get a list of profile audios for a user. Returns a :class:`aiogram.types.user_profile_audios.UserProfileAudios` object.

Source: https://core.telegram.org/bots/api#getuserprofileaudios

Parameters:
    user_id (``int``):
        Unique identifier of the target user

    offset (``int | None``):
        Sequential number of the first audio to be returned. By default, all audios are returned.

    limit (``int | None``):
        Limits the number of audios to be retrieved. Values between 1-100 are accepted. Defaults to 100.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``UserProfileAudios``: Returns a :class:`aiogram.types.user_profile_audios.UserProfileAudios` object.

---

### `get_user_profile_photos(user_id, offset, limit, request_timeout)`

Use this method to get a list of profile pictures for a user. Returns a :class:`aiogram.types.user_profile_photos.UserProfilePhotos` object.

Source: https://core.telegram.org/bots/api#getuserprofilephotos

Parameters:
    user_id (``int``):
        Unique identifier of the target user

    offset (``int | None``):
        Sequential number of the first photo to be returned. By default, all photos are returned.

    limit (``int | None``):
        Limits the number of photos to be retrieved. Values between 1-100 are accepted. Defaults to 100.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``UserProfilePhotos``: Returns a :class:`aiogram.types.user_profile_photos.UserProfilePhotos` object.

---

### `get_webhook_info(request_timeout)`

Use this method to get current webhook status. Requires no parameters. On success, returns a :class:`aiogram.types.webhook_info.WebhookInfo` object. If the bot is using :class:`aiogram.methods.get_updates.GetUpdates`, will return an object with the *url* field empty.

Source: https://core.telegram.org/bots/api#getwebhookinfo

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``WebhookInfo``: If the bot is using :class:`aiogram.methods.get_updates.GetUpdates`, will return an object with the *url* field empty.

---

### `gift_premium_subscription(user_id, month_count, star_count, text, text_parse_mode, text_entities, request_timeout)`

Gifts a Telegram Premium subscription to the given user. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#giftpremiumsubscription

Parameters:
    user_id (``int``):
        Unique identifier of the target user who will receive a Telegram Premium subscription

    month_count (``int``):
        Number of months the Telegram Premium subscription will be active for the user; must be one of 3, 6, or 12

    star_count (``int``):
        Number of Telegram Stars to pay for the Telegram Premium subscription; must be 1000 for 3 months, 1500 for 6 months, and 2500 for 12 months

    text (``str | None``):
        Text that will be shown along with the service message about the subscription; 0-128 characters

    text_parse_mode (``str | None``):
        Mode for parsing entities in the text. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details. Entities other than 'bold', 'italic', 'underline', 'strikethrough', 'spoiler', 'custom_emoji', and 'date_time' are ignored.

    text_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the gift text. It can be specified instead of *text_parse_mode*. Entities other than 'bold', 'italic', 'underline', 'strikethrough', 'spoiler', 'custom_emoji', and 'date_time' are ignored.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `hide_general_forum_topic(chat_id, request_timeout)`

Use this method to hide the 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights. The topic will be automatically closed if it was open. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#hidegeneralforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `leave_chat(chat_id, request_timeout)`

Use this method for your bot to leave a group, supergroup or channel. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#leavechat

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup or channel (in the format :code:`@channelusername`). Channel direct messages chats aren't supported; leave the corresponding channel instead.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `log_out(request_timeout)`

Use this method to log out from the cloud Bot API server before launching the bot locally. You **must** log out the bot before running it locally, otherwise there is no guarantee that the bot will receive updates. After a successful call, you can immediately log in on a local server, but will not be able to log in back to the cloud Bot API server for 10 minutes. Returns :code:`True` on success. Requires no parameters.

Source: https://core.telegram.org/bots/api#logout

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Requires no parameters.

---

### `me()`

Cached alias for getMe method

---

### `pin_chat_message(chat_id, message_id, business_connection_id, disable_notification, request_timeout)`

Use this method to add a message to the list of pinned messages in a chat. In private chats and channel direct messages chats, all non-service messages can be pinned. Conversely, the bot must be an administrator with the 'can_pin_messages' right or the 'can_edit_messages' right to pin messages in groups and channels respectively. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#pinchatmessage

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int``):
        Identifier of a message to pin

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be pinned

    disable_notification (``bool | None``):
        Pass :code:`True` if it is not necessary to send a notification to all chat members about the new pinned message. Notifications are always disabled in channels and private chats.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `post_story(business_connection_id, content, active_period, caption, parse_mode, caption_entities, areas, post_to_chat_page, protect_content, request_timeout)`

Posts a story on behalf of a managed business account. Requires the *can_manage_stories* business bot right. Returns :class:`aiogram.types.story.Story` on success.

Source: https://core.telegram.org/bots/api#poststory

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    content (``InputStoryContentUnion``):
        Content of the story

    active_period (``int``):
        Period after which the story is moved to the archive, in seconds; must be one of :code:`6 * 3600`, :code:`12 * 3600`, :code:`86400`, or :code:`2 * 86400`

    caption (``str | None``):
        Caption of the story, 0-2048 characters after entities parsing

    parse_mode (``str | None``):
        Mode for parsing entities in the story caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    areas (``list[StoryArea] | None``):
        A JSON-serialized list of clickable areas to be shown on the story

    post_to_chat_page (``bool | None``):
        Pass :code:`True` to keep the story accessible after it expires

    protect_content (``bool | None``):
        Pass :code:`True` if the content of the story must be protected from forwarding and screenshotting

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Story``: Returns :class:`aiogram.types.story.Story` on success.

---

### `promote_chat_member(chat_id, user_id, is_anonymous, can_manage_chat, can_delete_messages, can_manage_video_chats, can_restrict_members, can_promote_members, can_change_info, can_invite_users, can_post_stories, can_edit_stories, can_delete_stories, can_post_messages, can_edit_messages, can_pin_messages, can_manage_topics, can_manage_direct_messages, can_manage_tags, request_timeout)`

Use this method to promote or demote a user in a supergroup or a channel. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Pass :code:`False` for all boolean parameters to demote a user. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#promotechatmember

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    is_anonymous (``bool | None``):
        Pass :code:`True` if the administrator's presence in the chat is hidden

    can_manage_chat (``bool | None``):
        Pass :code:`True` if the administrator can access the chat event log, get boost list, see hidden supergroup and channel members, report spam messages, ignore slow mode, and send messages to the chat without paying Telegram Stars. Implied by any other administrator privilege.

    can_delete_messages (``bool | None``):
        Pass :code:`True` if the administrator can delete messages of other users

    can_manage_video_chats (``bool | None``):
        Pass :code:`True` if the administrator can manage video chats

    can_restrict_members (``bool | None``):
        Pass :code:`True` if the administrator can restrict, ban or unban chat members, or access supergroup statistics. For backward compatibility, defaults to :code:`True` for promotions of channel administrators

    can_promote_members (``bool | None``):
        Pass :code:`True` if the administrator can add new administrators with a subset of their own privileges or demote administrators that they have promoted, directly or indirectly (promoted by administrators that were appointed by him)

    can_change_info (``bool | None``):
        Pass :code:`True` if the administrator can change chat title, photo and other settings

    can_invite_users (``bool | None``):
        Pass :code:`True` if the administrator can invite new users to the chat

    can_post_stories (``bool | None``):
        Pass :code:`True` if the administrator can post stories to the chat

    can_edit_stories (``bool | None``):
        Pass :code:`True` if the administrator can edit stories posted by other users, post stories to the chat page, pin chat stories, and access the chat's story archive

    can_delete_stories (``bool | None``):
        Pass :code:`True` if the administrator can delete stories posted by other users

    can_post_messages (``bool | None``):
        Pass :code:`True` if the administrator can post messages in the channel, approve suggested posts, or access channel statistics; for channels only

    can_edit_messages (``bool | None``):
        Pass :code:`True` if the administrator can edit messages of other users and can pin messages; for channels only

    can_pin_messages (``bool | None``):
        Pass :code:`True` if the administrator can pin messages; for supergroups only

    can_manage_topics (``bool | None``):
        Pass :code:`True` if the user is allowed to create, rename, close, and reopen forum topics; for supergroups only

    can_manage_direct_messages (``bool | None``):
        Pass :code:`True` if the administrator can manage direct messages within the channel and decline suggested posts; for channels only

    can_manage_tags (``bool | None``):
        Pass :code:`True` if the administrator can edit the tags of regular members; for groups and supergroups only

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `read_business_message(business_connection_id, chat_id, message_id, request_timeout)`

Marks incoming message as read on behalf of a business account. Requires the *can_read_messages* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#readbusinessmessage

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection on behalf of which to read the message

    chat_id (``int``):
        Unique identifier of the chat in which the message was received. The chat must have been active in the last 24 hours.

    message_id (``int``):
        Unique identifier of the message to mark as read

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `refund_star_payment(user_id, telegram_payment_charge_id, request_timeout)`

Refunds a successful payment in `Telegram Stars <https://t.me/BotNews/90>`_. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#refundstarpayment

Parameters:
    user_id (``int``):
        Identifier of the user whose payment will be refunded

    telegram_payment_charge_id (``str``):
        Telegram payment identifier

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `remove_business_account_profile_photo(business_connection_id, is_public, request_timeout)`

Removes the current profile photo of a managed business account. Requires the *can_edit_profile_photo* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#removebusinessaccountprofilephoto

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    is_public (``bool | None``):
        Pass :code:`True` to remove the public photo, which is visible even if the main photo is hidden by the business account's privacy settings. After the main photo is removed, the previous profile photo (if present) becomes the main photo.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `remove_chat_verification(chat_id, request_timeout)`

Removes verification from a chat that is currently verified `on behalf of the organization <https://telegram.org/verify#third-party-verification>`_ represented by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#removechatverification

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `remove_my_profile_photo(request_timeout)`

Removes the profile photo of the bot. Requires no parameters. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#removemyprofilephoto

Parameters:
    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `remove_user_verification(user_id, request_timeout)`

Removes verification from a user who is currently verified `on behalf of the organization <https://telegram.org/verify#third-party-verification>`_ represented by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#removeuserverification

Parameters:
    user_id (``int``):
        Unique identifier of the target user

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `reopen_forum_topic(chat_id, message_thread_id, request_timeout)`

Use this method to reopen a closed topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights, unless it is the creator of the topic. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#reopenforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    message_thread_id (``int``):
        Unique identifier for the target message thread of the forum topic

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `reopen_general_forum_topic(chat_id, request_timeout)`

Use this method to reopen a closed 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights. The topic will be automatically unhidden if it was hidden. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#reopengeneralforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `replace_managed_bot_token(user_id, request_timeout)`

Use this method to revoke the current token of a managed bot and generate a new one. Returns the new token as *String* on success.

Source: https://core.telegram.org/bots/api#replacemanagedbottoken

Parameters:
    user_id (``int``):
        User identifier of the managed bot whose token will be replaced

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``str``: Returns the new token as *String* on success.

---

### `replace_sticker_in_set(user_id, name, old_sticker, sticker, request_timeout)`

Use this method to replace an existing sticker in a sticker set with a new one. The method is equivalent to calling :class:`aiogram.methods.delete_sticker_from_set.DeleteStickerFromSet`, then :class:`aiogram.methods.add_sticker_to_set.AddStickerToSet`, then :class:`aiogram.methods.set_sticker_position_in_set.SetStickerPositionInSet`. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#replacestickerinset

Parameters:
    user_id (``int``):
        User identifier of the sticker set owner

    name (``str``):
        Sticker set name

    old_sticker (``str``):
        File identifier of the replaced sticker

    sticker (``InputSticker``):
        A JSON-serialized object with information about the added sticker. If exactly the same sticker had already been added to the set, then the set remains unchanged.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `repost_story(business_connection_id, from_chat_id, from_story_id, active_period, post_to_chat_page, protect_content, request_timeout)`

Reposts a story on behalf of a business account from another business account. Both business accounts must be managed by the same bot, and the story on the source account must have been posted (or reposted) by the bot. Requires the *can_manage_stories* business bot right for both business accounts. Returns :class:`aiogram.types.story.Story` on success.

Source: https://core.telegram.org/bots/api#repoststory

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    from_chat_id (``int``):
        Unique identifier of the chat which posted the story that should be reposted

    from_story_id (``int``):
        Unique identifier of the story that should be reposted

    active_period (``int``):
        Period after which the story is moved to the archive, in seconds; must be one of :code:`6 * 3600`, :code:`12 * 3600`, :code:`86400`, or :code:`2 * 86400`

    post_to_chat_page (``bool | None``):
        Pass :code:`True` to keep the story accessible after it expires

    protect_content (``bool | None``):
        Pass :code:`True` if the content of the story must be protected from forwarding and screenshotting

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Story``: Returns :class:`aiogram.types.story.Story` on success.

---

### `restrict_chat_member(chat_id, user_id, permissions, use_independent_chat_permissions, until_date, request_timeout)`

Use this method to restrict a user in a supergroup. The bot must be an administrator in the supergroup for this to work and must have the appropriate administrator rights. Pass :code:`True` for all permissions to lift restrictions from a user. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#restrictchatmember

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    user_id (``int``):
        Unique identifier of the target user

    permissions (``ChatPermissions``):
        A JSON-serialized object for new user permissions

    use_independent_chat_permissions (``bool | None``):
        Pass :code:`True` if chat permissions are set independently. Otherwise, the *can_send_other_messages* and *can_add_web_page_previews* permissions will imply the *can_send_messages*, *can_send_audios*, *can_send_documents*, *can_send_photos*, *can_send_videos*, *can_send_video_notes*, and *can_send_voice_notes* permissions; the *can_send_polls* permission will imply the *can_send_messages* permission.

    until_date (``DateTimeUnion | None``):
        Date when restrictions will be lifted for the user; Unix time. If user is restricted for more than 366 days or less than 30 seconds from the current time, they are considered to be restricted forever

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `revoke_chat_invite_link(chat_id, invite_link, request_timeout)`

Use this method to revoke an invite link created by the bot. If the primary link is revoked, a new link is automatically generated. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns the revoked invite link as :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

Source: https://core.telegram.org/bots/api#revokechatinvitelink

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier of the target chat or username of the target channel (in the format :code:`@channelusername`)

    invite_link (``str``):
        The invite link to revoke

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``ChatInviteLink``: Returns the revoked invite link as :class:`aiogram.types.chat_invite_link.ChatInviteLink` object.

---

### `save_prepared_inline_message(user_id, result, allow_user_chats, allow_bot_chats, allow_group_chats, allow_channel_chats, request_timeout)`

Stores a message that can be sent by a user of a Mini App. Returns a :class:`aiogram.types.prepared_inline_message.PreparedInlineMessage` object.

Source: https://core.telegram.org/bots/api#savepreparedinlinemessage

Parameters:
    user_id (``int``):
        Unique identifier of the target user that can use the prepared message

    result (``InlineQueryResultUnion``):
        A JSON-serialized object describing the message to be sent

    allow_user_chats (``bool | None``):
        Pass :code:`True` if the message can be sent to private chats with users

    allow_bot_chats (``bool | None``):
        Pass :code:`True` if the message can be sent to private chats with bots

    allow_group_chats (``bool | None``):
        Pass :code:`True` if the message can be sent to group and supergroup chats

    allow_channel_chats (``bool | None``):
        Pass :code:`True` if the message can be sent to channel chats

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``PreparedInlineMessage``: Returns a :class:`aiogram.types.prepared_inline_message.PreparedInlineMessage` object.

---

### `save_prepared_keyboard_button(user_id, button, request_timeout)`

Stores a keyboard button that can be used by a user within a Mini App. Returns a :class:`aiogram.types.prepared_keyboard_button.PreparedKeyboardButton` object.

Source: https://core.telegram.org/bots/api#savepreparedkeyboardbutton

Parameters:
    user_id (``int``):
        Unique identifier of the target user that can use the button

    button (``KeyboardButton``):
        A JSON-serialized object describing the button to be saved. The button must be of the type *request_users*, *request_chat*, or *request_managed_bot*

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``PreparedKeyboardButton``: Returns a :class:`aiogram.types.prepared_keyboard_button.PreparedKeyboardButton` object.

---

### `send_animation(chat_id, animation, business_connection_id, message_thread_id, direct_messages_topic_id, duration, width, height, thumbnail, caption, parse_mode, caption_entities, show_caption_above_media, has_spoiler, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound). On success, the sent :class:`aiogram.types.message.Message` is returned. Bots can currently send animation files of up to 50 MB in size, this limit may be changed in the future.

Source: https://core.telegram.org/bots/api#sendanimation

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    animation (``InputFileUnion``):
        Animation to send. Pass a file_id as String to send an animation that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an animation from the Internet, or upload a new animation using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    duration (``int | None``):
        Duration of sent animation in seconds

    width (``int | None``):
        Animation width

    height (``int | None``):
        Animation height

    thumbnail (``InputFile | None``):
        Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can't be reused and can be only uploaded as a new file, so you can pass 'attach://<file_attach_name>' if the thumbnail was uploaded using multipart/form-data under <file_attach_name>. :ref:`More information on Sending Files » <sending-files>`

    caption (``str | None``):
        Animation caption (may also be used when resending animation by *file_id*), 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the animation caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    show_caption_above_media (``bool | Default | None``):
        Pass :code:`True`, if the caption must be shown above the message media

    has_spoiler (``bool | None``):
        Pass :code:`True` if the animation needs to be covered with a spoiler animation

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: Bots can currently send animation files of up to 50 MB in size, this limit may be changed in the future.

---

### `send_audio(chat_id, audio, business_connection_id, message_thread_id, direct_messages_topic_id, caption, parse_mode, caption_entities, duration, performer, title, thumbnail, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .MP3 or .M4A format. On success, the sent :class:`aiogram.types.message.Message` is returned. Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.
For sending voice messages, use the :class:`aiogram.methods.send_voice.SendVoice` method instead.

Source: https://core.telegram.org/bots/api#sendaudio

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    audio (``InputFileUnion``):
        Audio file to send. Pass a file_id as String to send an audio file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an audio file from the Internet, or upload a new one using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    caption (``str | None``):
        Audio caption, 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the audio caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    duration (``int | None``):
        Duration of the audio in seconds

    performer (``str | None``):
        Performer

    title (``str | None``):
        Track name

    thumbnail (``InputFile | None``):
        Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can't be reused and can be only uploaded as a new file, so you can pass 'attach://<file_attach_name>' if the thumbnail was uploaded using multipart/form-data under <file_attach_name>. :ref:`More information on Sending Files » <sending-files>`

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.

---

### `send_chat_action(chat_id, action, business_connection_id, message_thread_id, request_timeout)`

Use this method when you need to tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status). Returns :code:`True` on success.

 Example: The `ImageBot <https://t.me/imagebot>`_ needs some time to process a request and upload the image. Instead of sending a text message along the lines of 'Retrieving image, please wait…', the bot may use :class:`aiogram.methods.send_chat_action.SendChatAction` with *action* = *upload_photo*. The user will see a 'sending photo' status for the bot.

We only recommend using this method when a response from the bot will take a **noticeable** amount of time to arrive.

Source: https://core.telegram.org/bots/api#sendchataction

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`). Channel chats and channel direct messages chats aren't supported.

    action (``str``):
        Type of action to broadcast. Choose one, depending on what the user is about to receive: *typing* for `text messages <https://core.telegram.org/bots/api#sendmessage>`_, *upload_photo* for `photos <https://core.telegram.org/bots/api#sendphoto>`_, *record_video* or *upload_video* for `videos <https://core.telegram.org/bots/api#sendvideo>`_, *record_voice* or *upload_voice* for `voice notes <https://core.telegram.org/bots/api#sendvoice>`_, *upload_document* for `general files <https://core.telegram.org/bots/api#senddocument>`_, *choose_sticker* for `stickers <https://core.telegram.org/bots/api#sendsticker>`_, *find_location* for `location data <https://core.telegram.org/bots/api#sendlocation>`_, *record_video_note* or *upload_video_note* for `video notes <https://core.telegram.org/bots/api#sendvideonote>`_.

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the action will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread or topic of a forum; for supergroups and private chats of bots with forum topic mode enabled only

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: The user will see a 'sending photo' status for the bot.

---

### `send_checklist(business_connection_id, chat_id, checklist, disable_notification, protect_content, message_effect_id, reply_parameters, reply_markup, request_timeout)`

Use this method to send a checklist on behalf of a connected business account. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendchecklist

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection on behalf of which the message will be sent

    chat_id (``int``):
        Unique identifier for the target chat

    checklist (``InputChecklist``):
        A JSON-serialized object for the checklist to send

    disable_notification (``bool | None``):
        Sends the message silently. Users will receive a notification with no sound.

    protect_content (``bool | None``):
        Protects the contents of the sent message from forwarding and saving

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message

    reply_parameters (``ReplyParameters | None``):
        A JSON-serialized object for description of the message to reply to

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_contact(chat_id, phone_number, first_name, business_connection_id, message_thread_id, direct_messages_topic_id, last_name, vcard, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send phone contacts. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendcontact

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    phone_number (``str``):
        Contact's phone number

    first_name (``str``):
        Contact's first name

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    last_name (``str | None``):
        Contact's last name

    vcard (``str | None``):
        Additional data about the contact in the form of a `vCard <https://en.wikipedia.org/wiki/VCard>`_, 0-2048 bytes

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_dice(chat_id, business_connection_id, message_thread_id, direct_messages_topic_id, emoji, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send an animated emoji that will display a random value. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#senddice

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    emoji (``str | None``):
        Emoji on which the dice throw animation is based. Currently, must be one of '🎲', '🎯', '🏀', '⚽', '🎳', or '🎰'. Dice can have values 1-6 for '🎲', '🎯' and '🎳', values 1-5 for '🏀' and '⚽', and values 1-64 for '🎰'. Defaults to '🎲'

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_document(chat_id, document, business_connection_id, message_thread_id, direct_messages_topic_id, thumbnail, caption, parse_mode, caption_entities, disable_content_type_detection, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send general files. On success, the sent :class:`aiogram.types.message.Message` is returned. Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.

Source: https://core.telegram.org/bots/api#senddocument

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    document (``InputFileUnion``):
        File to send. Pass a file_id as String to send a file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    thumbnail (``InputFile | None``):
        Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can't be reused and can be only uploaded as a new file, so you can pass 'attach://<file_attach_name>' if the thumbnail was uploaded using multipart/form-data under <file_attach_name>. :ref:`More information on Sending Files » <sending-files>`

    caption (``str | None``):
        Document caption (may also be used when resending documents by *file_id*), 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the document caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    disable_content_type_detection (``bool | None``):
        Disables automatic server-side content type detection for files uploaded using multipart/form-data

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.

---

### `send_game(chat_id, game_short_name, business_connection_id, message_thread_id, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send a game. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendgame

Parameters:
    chat_id (``int``):
        Unique identifier for the target chat. Games can't be sent to channel direct messages chats and channel chats.

    game_short_name (``str``):
        Short name of the game, serves as the unique identifier for the game. Set up your games via `@BotFather <https://t.me/botfather>`_.

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_. If empty, one 'Play game_title' button will be shown. If not empty, the first button must launch the game.

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_gift(gift_id, user_id, chat_id, pay_for_upgrade, text, text_parse_mode, text_entities, request_timeout)`

Sends a gift to the given user or channel chat. The gift can't be converted to Telegram Stars by the receiver. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#sendgift

Parameters:
    gift_id (``str``):
        Identifier of the gift; limited gifts can't be sent to channel chats

    user_id (``int | None``):
        Required if *chat_id* is not specified. Unique identifier of the target user who will receive the gift.

    chat_id (``ChatIdUnion | None``):
        Required if *user_id* is not specified. Unique identifier for the chat or username of the channel (in the format :code:`@channelusername`) that will receive the gift.

    pay_for_upgrade (``bool | None``):
        Pass :code:`True` to pay for the gift upgrade from the bot's balance, thereby making the upgrade free for the receiver

    text (``str | None``):
        Text that will be shown along with the gift; 0-128 characters

    text_parse_mode (``str | None``):
        Mode for parsing entities in the text. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details. Entities other than 'bold', 'italic', 'underline', 'strikethrough', 'spoiler', 'custom_emoji', and 'date_time' are ignored.

    text_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the gift text. It can be specified instead of *text_parse_mode*. Entities other than 'bold', 'italic', 'underline', 'strikethrough', 'spoiler', 'custom_emoji', and 'date_time' are ignored.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `send_invoice(chat_id, title, description, payload, currency, prices, message_thread_id, direct_messages_topic_id, provider_token, max_tip_amount, suggested_tip_amounts, start_parameter, provider_data, photo_url, photo_size, photo_width, photo_height, need_name, need_phone_number, need_email, need_shipping_address, send_phone_number_to_provider, send_email_to_provider, is_flexible, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send invoices. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendinvoice

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    title (``str``):
        Product name, 1-32 characters

    description (``str``):
        Product description, 1-255 characters

    payload (``str``):
        Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use it for your internal processes.

    currency (``str``):
        Three-letter ISO 4217 currency code, see `more on currencies <https://core.telegram.org/bots/payments#supported-currencies>`_. Pass 'XTR' for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    prices (``list[LabeledPrice]``):
        Price breakdown, a JSON-serialized list of components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.). Must contain exactly one item for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    provider_token (``str | None``):
        Payment provider token, obtained via `@BotFather <https://t.me/botfather>`_. Pass an empty string for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    max_tip_amount (``int | None``):
        The maximum accepted amount for tips in the *smallest units* of the currency (integer, **not** float/double). For example, for a maximum tip of :code:`US$ 1.45` pass :code:`max_tip_amount = 145`. See the *exp* parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies). Defaults to 0. Not supported for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    suggested_tip_amounts (``list[int] | None``):
        A JSON-serialized array of suggested amounts of tips in the *smallest units* of the currency (integer, **not** float/double). At most 4 suggested tip amounts can be specified. The suggested tip amounts must be positive, passed in a strictly increased order and must not exceed *max_tip_amount*.

    start_parameter (``str | None``):
        Unique deep-linking parameter. If left empty, **forwarded copies** of the sent message will have a *Pay* button, allowing multiple users to pay directly from the forwarded message, using the same invoice. If non-empty, forwarded copies of the sent message will have a *URL* button with a deep link to the bot (instead of a *Pay* button), with the value used as the start parameter

    provider_data (``str | None``):
        JSON-serialized data about the invoice, which will be shared with the payment provider. A detailed description of required fields should be provided by the payment provider.

    photo_url (``str | None``):
        URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service. People like it better when they see what they are paying for.

    photo_size (``int | None``):
        Photo size in bytes

    photo_width (``int | None``):
        Photo width

    photo_height (``int | None``):
        Photo height

    need_name (``bool | None``):
        Pass :code:`True` if you require the user's full name to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    need_phone_number (``bool | None``):
        Pass :code:`True` if you require the user's phone number to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    need_email (``bool | None``):
        Pass :code:`True` if you require the user's email address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    need_shipping_address (``bool | None``):
        Pass :code:`True` if you require the user's shipping address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    send_phone_number_to_provider (``bool | None``):
        Pass :code:`True` if the user's phone number should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    send_email_to_provider (``bool | None``):
        Pass :code:`True` if the user's email address should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    is_flexible (``bool | None``):
        Pass :code:`True` if the final price depends on the shipping method. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_. If empty, one 'Pay :code:`total price`' button will be shown. If not empty, the first button must be a Pay button.

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_location(chat_id, latitude, longitude, business_connection_id, message_thread_id, direct_messages_topic_id, horizontal_accuracy, live_period, heading, proximity_alert_radius, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send point on the map. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendlocation

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    latitude (``float``):
        Latitude of the location

    longitude (``float``):
        Longitude of the location

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    horizontal_accuracy (``float | None``):
        The radius of uncertainty for the location, measured in meters; 0-1500

    live_period (``int | None``):
        Period in seconds during which the location will be updated (see `Live Locations <https://telegram.org/blog/live-locations>`_, should be between 60 and 86400, or 0x7FFFFFFF for live locations that can be edited indefinitely.

    heading (``int | None``):
        For live locations, a direction in which the user is moving, in degrees. Must be between 1 and 360 if specified.

    proximity_alert_radius (``int | None``):
        For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters. Must be between 1 and 100000 if specified.

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_media_group(chat_id, media, business_connection_id, message_thread_id, direct_messages_topic_id, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, reply_parameters, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send a group of photos, videos, documents or audios as an album. Documents and audio files can be only grouped in an album with messages of the same type. On success, an array of :class:`aiogram.types.message.Message` objects that were sent is returned.

Source: https://core.telegram.org/bots/api#sendmediagroup

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    media (``list[MediaUnion]``):
        A JSON-serialized array describing messages to be sent, must include 2-10 items

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the messages will be sent; required if the messages are sent to a direct messages chat

    disable_notification (``bool | None``):
        Sends messages `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent messages from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the messages are a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``list[Message]``: On success, an array of :class:`aiogram.types.message.Message` objects that were sent is returned.

---

### `send_message(chat_id, text, business_connection_id, message_thread_id, direct_messages_topic_id, parse_mode, entities, link_preview_options, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, disable_web_page_preview, reply_to_message_id, request_timeout)`

Use this method to send text messages. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendmessage

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    text (``str``):
        Text of the message to be sent, 1-4096 characters after entities parsing

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the message text. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in message text, which can be specified instead of *parse_mode*

    link_preview_options (``LinkPreviewOptions | Default | None``):
        Link preview generation options for the message

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    disable_web_page_preview (``bool | Default | None``):
        Disables link previews for links in this message

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_message_draft(chat_id, draft_id, text, message_thread_id, parse_mode, entities, request_timeout)`

Use this method to stream a partial message to a user while the message is being generated. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#sendmessagedraft

Parameters:
    chat_id (``int``):
        Unique identifier for the target private chat

    draft_id (``int``):
        Unique identifier of the message draft; must be non-zero. Changes of drafts with the same identifier are animated

    text (``str``):
        Text of the message to be sent, 1-4096 characters after entities parsing

    message_thread_id (``int | None``):
        Unique identifier for the target message thread

    parse_mode (``str | None``):
        Mode for parsing entities in the message text. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in message text, which can be specified instead of *parse_mode*

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `send_paid_media(chat_id, star_count, media, business_connection_id, message_thread_id, direct_messages_topic_id, payload, caption, parse_mode, caption_entities, show_caption_above_media, disable_notification, protect_content, allow_paid_broadcast, suggested_post_parameters, reply_parameters, reply_markup, request_timeout)`

Use this method to send paid media. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendpaidmedia

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`). If the chat is a channel, all Telegram Star proceeds from this media will be credited to the chat's balance. Otherwise, they will be credited to the bot's balance.

    star_count (``int``):
        The number of Telegram Stars that must be paid to buy access to the media; 1-25000

    media (``list[InputPaidMediaUnion]``):
        A JSON-serialized array describing the media to be sent; up to 10 items

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    payload (``str | None``):
        Bot-defined paid media payload, 0-128 bytes. This will not be displayed to the user, use it for your internal processes.

    caption (``str | None``):
        Media caption, 0-1024 characters after entities parsing

    parse_mode (``str | None``):
        Mode for parsing entities in the media caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    show_caption_above_media (``bool | None``):
        Pass :code:`True`, if the caption must be shown above the message media

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_photo(chat_id, photo, business_connection_id, message_thread_id, direct_messages_topic_id, caption, parse_mode, caption_entities, show_caption_above_media, has_spoiler, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send photos. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendphoto

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    photo (``InputFileUnion``):
        Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data. The photo must be at most 10 MB in size. The photo's width and height must not exceed 10000 in total. Width and height ratio must be at most 20. :ref:`More information on Sending Files » <sending-files>`

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    caption (``str | None``):
        Photo caption (may also be used when resending photos by *file_id*), 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the photo caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    show_caption_above_media (``bool | Default | None``):
        Pass :code:`True`, if the caption must be shown above the message media

    has_spoiler (``bool | None``):
        Pass :code:`True` if the photo needs to be covered with a spoiler animation

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_poll(chat_id, question, options, business_connection_id, message_thread_id, question_parse_mode, question_entities, is_anonymous, type, allows_multiple_answers, allows_revoting, shuffle_options, allow_adding_options, hide_results_until_closes, correct_option_ids, explanation, explanation_parse_mode, explanation_entities, open_period, close_date, is_closed, description, description_parse_mode, description_entities, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, reply_parameters, reply_markup, allow_sending_without_reply, correct_option_id, reply_to_message_id, request_timeout)`

Use this method to send a native poll. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendpoll

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`). Polls can't be sent to channel direct messages chats.

    question (``str``):
        Poll question, 1-300 characters

    options (``list[InputPollOptionUnion]``):
        A JSON-serialized list of 2-12 answer options

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    question_parse_mode (``str | Default | None``):
        Mode for parsing entities in the question. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details. Currently, only custom emoji entities are allowed

    question_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the poll question. It can be specified instead of *question_parse_mode*

    is_anonymous (``bool | None``):
        :code:`True`, if the poll needs to be anonymous, defaults to :code:`True`

    type (``str | None``):
        Poll type, 'quiz' or 'regular', defaults to 'regular'

    allows_multiple_answers (``bool | None``):
        Pass :code:`True`, if the poll allows multiple answers, defaults to :code:`False`

    allows_revoting (``bool | None``):
        Pass :code:`True`, if the poll allows to change chosen answer options, defaults to :code:`False` for quizzes and to :code:`True` for regular polls

    shuffle_options (``bool | None``):
        Pass :code:`True`, if the poll options must be shown in random order

    allow_adding_options (``bool | None``):
        Pass :code:`True`, if answer options can be added to the poll after creation; not supported for anonymous polls and quizzes

    hide_results_until_closes (``bool | None``):
        Pass :code:`True`, if poll results must be shown only after the poll closes

    correct_option_ids (``list[int] | None``):
        A JSON-serialized list of monotonically increasing 0-based identifiers of the correct answer options, required for polls in quiz mode

    explanation (``str | None``):
        Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style poll, 0-200 characters with at most 2 line feeds after entities parsing

    explanation_parse_mode (``str | Default | None``):
        Mode for parsing entities in the explanation. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    explanation_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the poll explanation. It can be specified instead of *explanation_parse_mode*

    open_period (``int | None``):
        Amount of time in seconds the poll will be active after creation, 5-2628000. Can't be used together with *close_date*.

    close_date (``DateTimeUnion | None``):
        Point in time (Unix timestamp) when the poll will be automatically closed. Must be at least 5 and no more than 2628000 seconds in the future. Can't be used together with *open_period*.

    is_closed (``bool | None``):
        Pass :code:`True` if the poll needs to be immediately closed. This can be useful for poll preview.

    description (``str | None``):
        Description of the poll to be sent, 0-1024 characters after entities parsing

    description_parse_mode (``str | Default | None``):
        Mode for parsing entities in the poll description. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    description_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the poll description, which can be specified instead of *description_parse_mode*

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    correct_option_id (``int | None``):
        0-based identifier of the correct answer option, required for polls in quiz mode

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_sticker(chat_id, sticker, business_connection_id, message_thread_id, direct_messages_topic_id, emoji, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send static .WEBP, `animated <https://telegram.org/blog/animated-stickers>`_ .TGS, or `video <https://telegram.org/blog/video-stickers-better-reactions>`_ .WEBM stickers. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendsticker

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    sticker (``InputFileUnion``):
        Sticker to send. Pass a file_id as String to send a file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a .WEBP sticker from the Internet, or upload a new .WEBP, .TGS, or .WEBM sticker using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`. Video and animated stickers can't be sent via an HTTP URL.

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    emoji (``str | None``):
        Emoji associated with the sticker; only for just uploaded stickers

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_venue(chat_id, latitude, longitude, title, address, business_connection_id, message_thread_id, direct_messages_topic_id, foursquare_id, foursquare_type, google_place_id, google_place_type, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send information about a venue. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendvenue

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    latitude (``float``):
        Latitude of the venue

    longitude (``float``):
        Longitude of the venue

    title (``str``):
        Name of the venue

    address (``str``):
        Address of the venue

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    foursquare_id (``str | None``):
        Foursquare identifier of the venue

    foursquare_type (``str | None``):
        Foursquare type of the venue, if known. (For example, 'arts_entertainment/default', 'arts_entertainment/aquarium' or 'food/icecream'.)

    google_place_id (``str | None``):
        Google Places identifier of the venue

    google_place_type (``str | None``):
        Google Places type of the venue. (See `supported types <https://developers.google.com/places/web-service/supported_types>`_.)

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_video(chat_id, video, business_connection_id, message_thread_id, direct_messages_topic_id, duration, width, height, thumbnail, cover, start_timestamp, caption, parse_mode, caption_entities, show_caption_above_media, has_spoiler, supports_streaming, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send video files, Telegram clients support MPEG4 videos (other formats may be sent as :class:`aiogram.types.document.Document`). On success, the sent :class:`aiogram.types.message.Message` is returned. Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.

Source: https://core.telegram.org/bots/api#sendvideo

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    video (``InputFileUnion``):
        Video to send. Pass a file_id as String to send a video that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a video from the Internet, or upload a new video using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    duration (``int | None``):
        Duration of sent video in seconds

    width (``int | None``):
        Video width

    height (``int | None``):
        Video height

    thumbnail (``InputFile | None``):
        Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can't be reused and can be only uploaded as a new file, so you can pass 'attach://<file_attach_name>' if the thumbnail was uploaded using multipart/form-data under <file_attach_name>. :ref:`More information on Sending Files » <sending-files>`

    cover (``InputFileUnion | None``):
        Cover for the video in the message. Pass a file_id to send a file that exists on the Telegram servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet, or pass 'attach://<file_attach_name>' to upload a new one using multipart/form-data under <file_attach_name> name. :ref:`More information on Sending Files » <sending-files>`

    start_timestamp (``DateTimeUnion | None``):
        Start timestamp for the video in the message

    caption (``str | None``):
        Video caption (may also be used when resending videos by *file_id*), 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the video caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    show_caption_above_media (``bool | Default | None``):
        Pass :code:`True`, if the caption must be shown above the message media

    has_spoiler (``bool | None``):
        Pass :code:`True` if the video needs to be covered with a spoiler animation

    supports_streaming (``bool | None``):
        Pass :code:`True` if the uploaded video is suitable for streaming

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.

---

### `send_video_note(chat_id, video_note, business_connection_id, message_thread_id, direct_messages_topic_id, duration, length, thumbnail, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

As of `v.4.0 <https://telegram.org/blog/video-messages-and-telescope>`_, Telegram clients support rounded square MPEG4 videos of up to 1 minute long. Use this method to send video messages. On success, the sent :class:`aiogram.types.message.Message` is returned.

Source: https://core.telegram.org/bots/api#sendvideonote

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    video_note (``InputFileUnion``):
        Video note to send. Pass a file_id as String to send a video note that exists on the Telegram servers (recommended) or upload a new video using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`. Sending video notes by a URL is currently unsupported

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    duration (``int | None``):
        Duration of sent video in seconds

    length (``int | None``):
        Video width and height, i.e. diameter of the video message

    thumbnail (``InputFile | None``):
        Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can't be reused and can be only uploaded as a new file, so you can pass 'attach://<file_attach_name>' if the thumbnail was uploaded using multipart/form-data under <file_attach_name>. :ref:`More information on Sending Files » <sending-files>`

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: On success, the sent :class:`aiogram.types.message.Message` is returned.

---

### `send_voice(chat_id, voice, business_connection_id, message_thread_id, direct_messages_topic_id, caption, parse_mode, caption_entities, duration, disable_notification, protect_content, allow_paid_broadcast, message_effect_id, suggested_post_parameters, reply_parameters, reply_markup, allow_sending_without_reply, reply_to_message_id, request_timeout)`

Use this method to send audio files, if you want Telegram clients to display the file as a playable voice message. For this to work, your audio must be in an .OGG file encoded with OPUS, or in .MP3 format, or in .M4A format (other formats may be sent as :class:`aiogram.types.audio.Audio` or :class:`aiogram.types.document.Document`). On success, the sent :class:`aiogram.types.message.Message` is returned. Bots can currently send voice messages of up to 50 MB in size, this limit may be changed in the future.

Source: https://core.telegram.org/bots/api#sendvoice

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    voice (``InputFileUnion``):
        Audio file to send. Pass a file_id as String to send a file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be sent

    message_thread_id (``int | None``):
        Unique identifier for the target message thread (topic) of a forum; for forum supergroups and private chats of bots with forum topic mode enabled only

    direct_messages_topic_id (``int | None``):
        Identifier of the direct messages topic to which the message will be sent; required if the message is sent to a direct messages chat

    caption (``str | None``):
        Voice message caption, 0-1024 characters after entities parsing

    parse_mode (``str | Default | None``):
        Mode for parsing entities in the voice message caption. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.

    caption_entities (``list[MessageEntity] | None``):
        A JSON-serialized list of special entities that appear in the caption, which can be specified instead of *parse_mode*

    duration (``int | None``):
        Duration of the voice message in seconds

    disable_notification (``bool | None``):
        Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.

    protect_content (``bool | Default | None``):
        Protects the contents of the sent message from forwarding and saving

    allow_paid_broadcast (``bool | None``):
        Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance

    message_effect_id (``str | None``):
        Unique identifier of the message effect to be added to the message; for private chats only

    suggested_post_parameters (``SuggestedPostParameters | None``):
        A JSON-serialized object containing the parameters of the suggested post to send; for direct messages chats only. If the message is sent as a reply to another suggested post, then that suggested post is automatically declined.

    reply_parameters (``ReplyParameters | None``):
        Description of the message to reply to

    reply_markup (``ReplyMarkupUnion | None``):
        Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user

    allow_sending_without_reply (``bool | None``):
        Pass :code:`True` if the message should be sent even if the specified replied-to message is not found

    reply_to_message_id (``int | None``):
        If the message is a reply, ID of the original message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message``: Bots can currently send voice messages of up to 50 MB in size, this limit may be changed in the future.

---

### `set_business_account_bio(business_connection_id, bio, request_timeout)`

Changes the bio of a managed business account. Requires the *can_change_bio* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setbusinessaccountbio

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    bio (``str | None``):
        The new value of the bio for the business account; 0-140 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_business_account_gift_settings(business_connection_id, show_gift_button, accepted_gift_types, request_timeout)`

Changes the privacy settings pertaining to incoming gifts in a managed business account. Requires the *can_change_gift_settings* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setbusinessaccountgiftsettings

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    show_gift_button (``bool``):
        Pass :code:`True`, if a button for sending a gift to the user or by the business account must always be shown in the input field

    accepted_gift_types (``AcceptedGiftTypes``):
        Types of gifts accepted by the business account

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_business_account_name(business_connection_id, first_name, last_name, request_timeout)`

Changes the first and last name of a managed business account. Requires the *can_change_name* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setbusinessaccountname

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    first_name (``str``):
        The new value of the first name for the business account; 1-64 characters

    last_name (``str | None``):
        The new value of the last name for the business account; 0-64 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_business_account_profile_photo(business_connection_id, photo, is_public, request_timeout)`

Changes the profile photo of a managed business account. Requires the *can_edit_profile_photo* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setbusinessaccountprofilephoto

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    photo (``InputProfilePhotoUnion``):
        The new profile photo to set

    is_public (``bool | None``):
        Pass :code:`True` to set the public photo, which will be visible even if the main photo is hidden by the business account's privacy settings. An account can have only one public photo.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_business_account_username(business_connection_id, username, request_timeout)`

Changes the username of a managed business account. Requires the *can_change_username* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setbusinessaccountusername

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    username (``str | None``):
        The new value of the username for the business account; 0-32 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_administrator_custom_title(chat_id, user_id, custom_title, request_timeout)`

Use this method to set a custom title for an administrator in a supergroup promoted by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatadministratorcustomtitle

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    user_id (``int``):
        Unique identifier of the target user

    custom_title (``str``):
        New custom title for the administrator; 0-16 characters, emoji are not allowed

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_description(chat_id, description, request_timeout)`

Use this method to change the description of a group, a supergroup or a channel. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatdescription

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    description (``str | None``):
        New chat description, 0-255 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_member_tag(chat_id, user_id, tag, request_timeout)`

Use this method to set a tag for a regular member in a group or a supergroup. The bot must be an administrator in the chat for this to work and must have the *can_manage_tags* administrator right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatmembertag

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    user_id (``int``):
        Unique identifier of the target user

    tag (``str | None``):
        New tag for the member; 0-16 characters, emoji are not allowed

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_menu_button(chat_id, menu_button, request_timeout)`

Use this method to change the bot's menu button in a private chat, or the default menu button. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatmenubutton

Parameters:
    chat_id (``int | None``):
        Unique identifier for the target private chat. If not specified, default bot's menu button will be changed

    menu_button (``MenuButtonUnion | None``):
        A JSON-serialized object for the bot's new menu button. Defaults to :class:`aiogram.types.menu_button_default.MenuButtonDefault`

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_permissions(chat_id, permissions, use_independent_chat_permissions, request_timeout)`

Use this method to set default chat permissions for all members. The bot must be an administrator in the group or a supergroup for this to work and must have the *can_restrict_members* administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatpermissions

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    permissions (``ChatPermissions``):
        A JSON-serialized object for new default chat permissions

    use_independent_chat_permissions (``bool | None``):
        Pass :code:`True` if chat permissions are set independently. Otherwise, the *can_send_other_messages* and *can_add_web_page_previews* permissions will imply the *can_send_messages*, *can_send_audios*, *can_send_documents*, *can_send_photos*, *can_send_videos*, *can_send_video_notes*, and *can_send_voice_notes* permissions; the *can_send_polls* permission will imply the *can_send_messages* permission.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_photo(chat_id, photo, request_timeout)`

Use this method to set a new profile photo for the chat. Photos can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatphoto

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    photo (``InputFile``):
        New chat photo, uploaded using multipart/form-data

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_sticker_set(chat_id, sticker_set_name, request_timeout)`

Use this method to set a new group sticker set for a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Use the field *can_set_sticker_set* optionally returned in :class:`aiogram.methods.get_chat.GetChat` requests to check if the bot can use this method. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchatstickerset

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    sticker_set_name (``str``):
        Name of the sticker set to be set as the group sticker set

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_chat_title(chat_id, title, request_timeout)`

Use this method to change the title of a chat. Titles can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setchattitle

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    title (``str``):
        New chat title, 1-128 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_custom_emoji_sticker_set_thumbnail(name, custom_emoji_id, request_timeout)`

Use this method to set the thumbnail of a custom emoji sticker set. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setcustomemojistickersetthumbnail

Parameters:
    name (``str``):
        Sticker set name

    custom_emoji_id (``str | None``):
        Custom emoji identifier of a sticker from the sticker set; pass an empty string to drop the thumbnail and use the first sticker as the thumbnail.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_game_score(user_id, score, force, disable_edit_message, chat_id, message_id, inline_message_id, request_timeout)`

Use this method to set the score of the specified user in a game message. On success, if the message is not an inline message, the :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned. Returns an error, if the new score is not greater than the user's current score in the chat and *force* is :code:`False`.

Source: https://core.telegram.org/bots/api#setgamescore

Parameters:
    user_id (``int``):
        User identifier

    score (``int``):
        New score, must be non-negative

    force (``bool | None``):
        Pass :code:`True` if the high score is allowed to decrease. This can be useful when fixing mistakes or banning cheaters

    disable_edit_message (``bool | None``):
        Pass :code:`True` if the game message should not be automatically edited to include the current scoreboard

    chat_id (``int | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the sent message

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: Returns an error, if the new score is not greater than the user's current score in the chat and *force* is :code:`False`.

---

### `set_message_reaction(chat_id, message_id, reaction, is_big, request_timeout)`

Use this method to change the chosen reactions on a message. Service messages of some types can't be reacted to. Automatically forwarded messages from a channel to its discussion group have the same available reactions as messages in the channel. Bots can't use paid reactions. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmessagereaction

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int``):
        Identifier of the target message. If the message belongs to a media group, the reaction is set to the first non-deleted message in the group instead.

    reaction (``list[ReactionTypeUnion] | None``):
        A JSON-serialized list of reaction types to set on the message. Currently, as non-premium users, bots can set up to one reaction per message. A custom emoji reaction can be used if it is either already present on the message or explicitly allowed by chat administrators. Paid reactions can't be used by bots.

    is_big (``bool | None``):
        Pass :code:`True` to set the reaction with a big animation

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_my_commands(commands, scope, language_code, request_timeout)`

Use this method to change the list of the bot's commands. See `this manual <https://core.telegram.org/bots/features#commands>`_ for more details about bot commands. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmycommands

Parameters:
    commands (``list[BotCommand]``):
        A JSON-serialized list of bot commands to be set as the list of the bot's commands. At most 100 commands can be specified.

    scope (``BotCommandScopeUnion | None``):
        A JSON-serialized object, describing scope of users for which the commands are relevant. Defaults to :class:`aiogram.types.bot_command_scope_default.BotCommandScopeDefault`.

    language_code (``str | None``):
        A two-letter ISO 639-1 language code. If empty, commands will be applied to all users from the given scope, for whose language there are no dedicated commands

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_my_default_administrator_rights(rights, for_channels, request_timeout)`

Use this method to change the default administrator rights requested by the bot when it's added as an administrator to groups or channels. These rights will be suggested to users, but they are free to modify the list before adding the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmydefaultadministratorrights

Parameters:
    rights (``ChatAdministratorRights | None``):
        A JSON-serialized object describing new default administrator rights. If not specified, the default administrator rights will be cleared.

    for_channels (``bool | None``):
        Pass :code:`True` to change the default administrator rights of the bot in channels. Otherwise, the default administrator rights of the bot for groups and supergroups will be changed.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_my_description(description, language_code, request_timeout)`

Use this method to change the bot's description, which is shown in the chat with the bot if the chat is empty. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmydescription

Parameters:
    description (``str | None``):
        New bot description; 0-512 characters. Pass an empty string to remove the dedicated description for the given language.

    language_code (``str | None``):
        A two-letter ISO 639-1 language code. If empty, the description will be applied to all users for whose language there is no dedicated description.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_my_name(name, language_code, request_timeout)`

Use this method to change the bot's name. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmyname

Parameters:
    name (``str | None``):
        New bot name; 0-64 characters. Pass an empty string to remove the dedicated name for the given language.

    language_code (``str | None``):
        A two-letter ISO 639-1 language code. If empty, the name will be shown to all users for whose language there is no dedicated name.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_my_profile_photo(photo, request_timeout)`

Changes the profile photo of the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmyprofilephoto

Parameters:
    photo (``InputProfilePhotoUnion``):
        The new profile photo to set

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_my_short_description(short_description, language_code, request_timeout)`

Use this method to change the bot's short description, which is shown on the bot's profile page and is sent together with the link when users share the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setmyshortdescription

Parameters:
    short_description (``str | None``):
        New short description for the bot; 0-120 characters. Pass an empty string to remove the dedicated short description for the given language.

    language_code (``str | None``):
        A two-letter ISO 639-1 language code. If empty, the short description will be applied to all users for whose language there is no dedicated short description.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_passport_data_errors(user_id, errors, request_timeout)`

Informs a user that some of the Telegram Passport elements they provided contains errors. The user will not be able to re-submit their Passport to you until the errors are fixed (the contents of the field for which you returned the error must change). Returns :code:`True` on success.
Use this if the data submitted by the user doesn't satisfy the standards your service requires for any reason. For example, if a birthday date seems invalid, a submitted document is blurry, a scan shows evidence of tampering, etc. Supply some details in the error message to make sure the user knows how to correct the issues.

Source: https://core.telegram.org/bots/api#setpassportdataerrors

Parameters:
    user_id (``int``):
        User identifier

    errors (``list[PassportElementErrorUnion]``):
        A JSON-serialized array describing the errors

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Supply some details in the error message to make sure the user knows how to correct the issues.

---

### `set_sticker_emoji_list(sticker, emoji_list, request_timeout)`

Use this method to change the list of emoji assigned to a regular or custom emoji sticker. The sticker must belong to a sticker set created by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setstickeremojilist

Parameters:
    sticker (``str``):
        File identifier of the sticker

    emoji_list (``list[str]``):
        A JSON-serialized list of 1-20 emoji associated with the sticker

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_sticker_keywords(sticker, keywords, request_timeout)`

Use this method to change search keywords assigned to a regular or custom emoji sticker. The sticker must belong to a sticker set created by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setstickerkeywords

Parameters:
    sticker (``str``):
        File identifier of the sticker

    keywords (``list[str] | None``):
        A JSON-serialized list of 0-20 search keywords for the sticker with total length of up to 64 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_sticker_mask_position(sticker, mask_position, request_timeout)`

Use this method to change the `mask position <https://core.telegram.org/bots/api#maskposition>`_ of a mask sticker. The sticker must belong to a sticker set that was created by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setstickermaskposition

Parameters:
    sticker (``str``):
        File identifier of the sticker

    mask_position (``MaskPosition | None``):
        A JSON-serialized object with the position where the mask should be placed on faces. Omit the parameter to remove the mask position.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_sticker_position_in_set(sticker, position, request_timeout)`

Use this method to move a sticker in a set created by the bot to a specific position. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setstickerpositioninset

Parameters:
    sticker (``str``):
        File identifier of the sticker

    position (``int``):
        New sticker position in the set, zero-based

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_sticker_set_thumbnail(name, user_id, format, thumbnail, request_timeout)`

Use this method to set the thumbnail of a regular or mask sticker set. The format of the thumbnail file must match the format of the stickers in the set. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setstickersetthumbnail

Parameters:
    name (``str``):
        Sticker set name

    user_id (``int``):
        User identifier of the sticker set owner

    format (``str``):
        Format of the thumbnail, must be one of 'static' for a **.WEBP** or **.PNG** image, 'animated' for a **.TGS** animation, or 'video' for a **.WEBM** video

    thumbnail (``InputFileUnion | None``):
        A **.WEBP** or **.PNG** image with the thumbnail, must be up to 128 kilobytes in size and have a width and height of exactly 100px, or a **.TGS** animation with a thumbnail up to 32 kilobytes in size (see `https://core.telegram.org/stickers#animation-requirements <https://core.telegram.org/stickers#animation-requirements>`_`https://core.telegram.org/stickers#animation-requirements <https://core.telegram.org/stickers#animation-requirements>`_ for animated sticker technical requirements), or a **.WEBM** video with the thumbnail up to 32 kilobytes in size; see `https://core.telegram.org/stickers#video-requirements <https://core.telegram.org/stickers#video-requirements>`_`https://core.telegram.org/stickers#video-requirements <https://core.telegram.org/stickers#video-requirements>`_ for video sticker technical requirements. Pass a *file_id* as a String to send a file that already exists on the Telegram servers, pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one using multipart/form-data. :ref:`More information on Sending Files » <sending-files>`. Animated and video sticker set thumbnails can't be uploaded via HTTP URL. If omitted, then the thumbnail is dropped and the first sticker is used as the thumbnail.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_sticker_set_title(name, title, request_timeout)`

Use this method to set the title of a created sticker set. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setstickersettitle

Parameters:
    name (``str``):
        Sticker set name

    title (``str``):
        Sticker set title, 1-64 characters

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_user_emoji_status(user_id, emoji_status_custom_emoji_id, emoji_status_expiration_date, request_timeout)`

Changes the emoji status for a given user that previously allowed the bot to manage their emoji status via the Mini App method `requestEmojiStatusAccess <https://core.telegram.org/bots/webapps#initializing-mini-apps>`_. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#setuseremojistatus

Parameters:
    user_id (``int``):
        Unique identifier of the target user

    emoji_status_custom_emoji_id (``str | None``):
        Custom emoji identifier of the emoji status to set. Pass an empty string to remove the status.

    emoji_status_expiration_date (``DateTimeUnion | None``):
        Expiration date of the emoji status, if any

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `set_webhook(url, certificate, ip_address, max_connections, allowed_updates, drop_pending_updates, secret_token, request_timeout)`

Use this method to specify a URL and receive incoming updates via an outgoing webhook. Whenever there is an update for the bot, we will send an HTTPS POST request to the specified URL, containing a JSON-serialized :class:`aiogram.types.update.Update`. In case of an unsuccessful request (a request with response `HTTP status code <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes>`_ different from :code:`2XY`), we will repeat the request and give up after a reasonable amount of attempts. Returns :code:`True` on success.
If you'd like to make sure that the webhook was set by you, you can specify secret data in the parameter *secret_token*. If specified, the request will contain a header 'X-Telegram-Bot-Api-Secret-Token' with the secret token as content.

 **Notes**

 **1.** You will not be able to receive updates using :class:`aiogram.methods.get_updates.GetUpdates` for as long as an outgoing webhook is set up.

 **2.** To use a self-signed certificate, you need to upload your `public key certificate <https://core.telegram.org/bots/self-signed>`_ using *certificate* parameter. Please upload as InputFile, sending a String will not work.

 **3.** Ports currently supported *for webhooks*: **443, 80, 88, 8443**.
 If you're having any trouble setting up webhooks, please check out this `amazing guide to webhooks <https://core.telegram.org/bots/webhooks>`_.

Source: https://core.telegram.org/bots/api#setwebhook

Parameters:
    url (``str``):
        HTTPS URL to send updates to. Use an empty string to remove webhook integration

    certificate (``InputFile | None``):
        Upload your public key certificate so that the root certificate in use can be checked. See our `self-signed guide <https://core.telegram.org/bots/self-signed>`_ for details.

    ip_address (``str | None``):
        The fixed IP address which will be used to send webhook requests instead of the IP address resolved through DNS

    max_connections (``int | None``):
        The maximum allowed number of simultaneous HTTPS connections to the webhook for update delivery, 1-100. Defaults to *40*. Use lower values to limit the load on your bot's server, and higher values to increase your bot's throughput.

    allowed_updates (``list[str] | None``):
        A JSON-serialized list of the update types you want your bot to receive. For example, specify :code:`["message", "edited_channel_post", "callback_query"]` to only receive updates of these types. See :class:`aiogram.types.update.Update` for a complete list of available update types. Specify an empty list to receive all update types except *chat_member*, *message_reaction*, and *message_reaction_count* (default). If not specified, the previous setting will be used.

    drop_pending_updates (``bool | None``):
        Pass :code:`True` to drop all pending updates

    secret_token (``str | None``):
        A secret token to be sent in a header 'X-Telegram-Bot-Api-Secret-Token' in every webhook request, 1-256 characters. Only characters :code:`A-Z`, :code:`a-z`, :code:`0-9`, :code:`_` and :code:`-` are allowed. The header is useful to ensure that the request comes from a webhook set by you.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Please upload as InputFile, sending a String will not work.

---

### `stop_message_live_location(business_connection_id, chat_id, message_id, inline_message_id, reply_markup, request_timeout)`

Use this method to stop updating a live location message before *live_period* expires. On success, if the message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned.

Source: https://core.telegram.org/bots/api#stopmessagelivelocation

Parameters:
    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    chat_id (``ChatIdUnion | None``):
        Required if *inline_message_id* is not specified. Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int | None``):
        Required if *inline_message_id* is not specified. Identifier of the message with live location to stop

    inline_message_id (``str | None``):
        Required if *chat_id* and *message_id* are not specified. Identifier of the inline message

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for a new `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Message | bool``: On success, if the message is not an inline message, the edited :class:`aiogram.types.message.Message` is returned, otherwise :code:`True` is returned.

---

### `stop_poll(chat_id, message_id, business_connection_id, reply_markup, request_timeout)`

Use this method to stop a poll which was sent by the bot. On success, the stopped :class:`aiogram.types.poll.Poll` is returned.

Source: https://core.telegram.org/bots/api#stoppoll

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    message_id (``int``):
        Identifier of the original message with the poll

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message to be edited was sent

    reply_markup (``InlineKeyboardMarkup | None``):
        A JSON-serialized object for a new message `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``Poll``: On success, the stopped :class:`aiogram.types.poll.Poll` is returned.

---

### `transfer_business_account_stars(business_connection_id, star_count, request_timeout)`

Transfers Telegram Stars from the business account balance to the bot's balance. Requires the *can_transfer_stars* business bot right. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#transferbusinessaccountstars

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    star_count (``int``):
        Number of Telegram Stars to transfer; 1-10000

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `transfer_gift(business_connection_id, owned_gift_id, new_owner_chat_id, star_count, request_timeout)`

Transfers an owned unique gift to another user. Requires the *can_transfer_and_upgrade_gifts* business bot right. Requires *can_transfer_stars* business bot right if the transfer is paid. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#transfergift

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    owned_gift_id (``str``):
        Unique identifier of the regular gift that should be transferred

    new_owner_chat_id (``int``):
        Unique identifier of the chat which will own the gift. The chat must be active in the last 24 hours.

    star_count (``int | None``):
        The amount of Telegram Stars that will be paid for the transfer from the business account balance. If positive, then the *can_transfer_stars* business bot right is required.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unban_chat_member(chat_id, user_id, only_if_banned, request_timeout)`

Use this method to unban a previously banned user in a supergroup or channel. The user will **not** return to the group or channel automatically, but will be able to join via link, etc. The bot must be an administrator for this to work. By default, this method guarantees that after the call the user is not a member of the chat, but will be able to join it. So if the user is a member of the chat they will also be **removed** from the chat. If you don't want this, use the parameter *only_if_banned*. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unbanchatmember

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target group or username of the target supergroup or channel (in the format :code:`@channelusername`)

    user_id (``int``):
        Unique identifier of the target user

    only_if_banned (``bool | None``):
        Do nothing if the user is not banned

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unban_chat_sender_chat(chat_id, sender_chat_id, request_timeout)`

Use this method to unban a previously banned channel chat in a supergroup or channel. The bot must be an administrator for this to work and must have the appropriate administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unbanchatsenderchat

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    sender_chat_id (``int``):
        Unique identifier of the target sender chat

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unhide_general_forum_topic(chat_id, request_timeout)`

Use this method to unhide the 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the *can_manage_topics* administrator rights. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unhidegeneralforumtopic

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unpin_all_chat_messages(chat_id, request_timeout)`

Use this method to clear the list of pinned messages in a chat. In private chats and channel direct messages chats, no additional rights are required to unpin all pinned messages. Conversely, the bot must be an administrator with the 'can_pin_messages' right or the 'can_edit_messages' right to unpin all pinned messages in groups and channels respectively. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unpinallchatmessages

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unpin_all_forum_topic_messages(chat_id, message_thread_id, request_timeout)`

Use this method to clear the list of pinned messages in a forum topic in a forum supergroup chat or a private chat with a user. In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the *can_pin_messages* administrator right in the supergroup. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unpinallforumtopicmessages

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    message_thread_id (``int``):
        Unique identifier for the target message thread of the forum topic

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unpin_all_general_forum_topic_messages(chat_id, request_timeout)`

Use this method to clear the list of pinned messages in a General forum topic. The bot must be an administrator in the chat for this to work and must have the *can_pin_messages* administrator right in the supergroup. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unpinallgeneralforumtopicmessages

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target supergroup (in the format :code:`@supergroupusername`)

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `unpin_chat_message(chat_id, business_connection_id, message_id, request_timeout)`

Use this method to remove a message from the list of pinned messages in a chat. In private chats and channel direct messages chats, all messages can be unpinned. Conversely, the bot must be an administrator with the 'can_pin_messages' right or the 'can_edit_messages' right to unpin messages in groups and channels respectively. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#unpinchatmessage

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`)

    business_connection_id (``str | None``):
        Unique identifier of the business connection on behalf of which the message will be unpinned

    message_id (``int | None``):
        Identifier of the message to unpin. Required if *business_connection_id* is specified. If not specified, the most recent pinned message (by sending date) will be unpinned.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `upgrade_gift(business_connection_id, owned_gift_id, keep_original_details, star_count, request_timeout)`

Upgrades a given regular gift to a unique gift. Requires the *can_transfer_and_upgrade_gifts* business bot right. Additionally requires the *can_transfer_stars* business bot right if the upgrade is paid. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#upgradegift

Parameters:
    business_connection_id (``str``):
        Unique identifier of the business connection

    owned_gift_id (``str``):
        Unique identifier of the regular gift that should be upgraded to a unique one

    keep_original_details (``bool | None``):
        Pass :code:`True` to keep the original gift text, sender and receiver in the upgraded gift

    star_count (``int | None``):
        The amount of Telegram Stars that will be paid for the upgrade from the business account balance. If :code:`gift.prepaid_upgrade_star_count > 0`, then pass 0, otherwise, the *can_transfer_stars* business bot right is required and :code:`gift.upgrade_star_count` must be passed.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `upload_sticker_file(user_id, sticker, sticker_format, request_timeout)`

Use this method to upload a file with a sticker for later use in the :class:`aiogram.methods.create_new_sticker_set.CreateNewStickerSet`, :class:`aiogram.methods.add_sticker_to_set.AddStickerToSet`, or :class:`aiogram.methods.replace_sticker_in_set.ReplaceStickerInSet` methods (the file can be used multiple times). Returns the uploaded :class:`aiogram.types.file.File` on success.

Source: https://core.telegram.org/bots/api#uploadstickerfile

Parameters:
    user_id (``int``):
        User identifier of sticker file owner

    sticker (``InputFile``):
        A file with the sticker in .WEBP, .PNG, .TGS, or .WEBM format. See `https://core.telegram.org/stickers <https://core.telegram.org/stickers>`_`https://core.telegram.org/stickers <https://core.telegram.org/stickers>`_ for technical requirements. :ref:`More information on Sending Files » <sending-files>`

    sticker_format (``str``):
        Format of the sticker, must be one of 'static', 'animated', 'video'

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``File``: Returns the uploaded :class:`aiogram.types.file.File` on success.

---

### `verify_chat(chat_id, custom_description, request_timeout)`

Verifies a chat `on behalf of the organization <https://telegram.org/verify#third-party-verification>`_ which is represented by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#verifychat

Parameters:
    chat_id (``ChatIdUnion``):
        Unique identifier for the target chat or username of the target channel (in the format :code:`@channelusername`). Channel direct messages chats can't be verified.

    custom_description (``str | None``):
        Custom description for the verification; 0-70 characters. Must be empty if the organization isn't allowed to provide a custom verification description.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---

### `verify_user(user_id, custom_description, request_timeout)`

Verifies a user `on behalf of the organization <https://telegram.org/verify#third-party-verification>`_ which is represented by the bot. Returns :code:`True` on success.

Source: https://core.telegram.org/bots/api#verifyuser

Parameters:
    user_id (``int``):
        Unique identifier of the target user

    custom_description (``str | None``):
        Custom description for the verification; 0-70 characters. Must be empty if the organization isn't allowed to provide a custom verification description.

    request_timeout (``int | None``):
        Request timeout

Returns:
    ``bool``: Returns :code:`True` on success.

---
