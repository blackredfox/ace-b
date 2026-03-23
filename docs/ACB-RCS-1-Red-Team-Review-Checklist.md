ACE-B / RCS-1 — Red-Team Review Checklist
0. Killer Question (главный тест)

“Если убрать красивое описание — останется ли это просто игрушкой?”

Если ответ “да” → мы в зоне риска.

🧠 1. Concept Validity (не псевдонаука ли это?)
❌ Судья атакует:

“Почему это вообще интеллект? Это просто pattern switching.”

Проверка:
 Мы чётко формулируем:
что именно является когнитивной способностью
 Есть связь с:
learning under distribution shift
belief revision
policy update under uncertainty
 Мы не используем расплывчатые слова типа:
“understanding”, “reasoning” без операционализации
🔥 Если нет:

→ это выглядит как toy task с умными словами

⚙️ 2. Behavioral Signal (есть ли реальный сигнал?)
❌ Судья атакует:

“Ваш benchmark не различает модели, он просто считает accuracy.”

Проверка:
 Метрики разделяют типы поведения, а не просто успех:
learning vs guessing
slow vs fast adaptation
confusion vs perseveration
 Есть trajectory-level анализ, а не только итог
 Есть минимум 3 baseline-а, которые дают разные профили
🔥 Критический пункт:
 Perseveration Rate реально что-то ловит, а не дублирует accuracy

Если нет → это слабое место

🧪 3. Non-Triviality (не решается ли это тупо?)
❌ Судья атакует:

“Это можно зашить в 20 строках кода.”

Проверка:
 Есть несколько rule families (не один shift)
 Есть ambiguity до switch
 Есть false hypotheses, которые выглядят правдоподобно
 Нельзя решить через:
lookup
memorization
trivial heuristic
🔥 Если можно:

→ benchmark мёртв

🛡 4. Anti-Cheating Strength
❌ Судья атакует:

“Я могу переобучить модель под ваш benchmark.”

Проверка:
 procedural generation
 hidden seeds
 variable switch timing
 unseen parameter combinations
 train ≠ test distribution
🔥 Вопрос-ловушка:

“Если я дам вам 10k эпизодов, сможете ли вы overfit?”

Если “да” → проблема

🔁 5. Generalization Claim
❌ Судья атакует:

“Это не AGI, это узкий тест.”

Проверка:
 Мы НЕ утверждаем “AGI benchmark”

 Мы чётко говорим:

“This evaluates one specific capability slice”

 Есть мост к:
real agent failures
non-stationary environments
production systems
🧩 6. External Validity (самое важное для победы)
❌ Судья атакует:

“Где это вообще используется?”

Проверка:
 Есть реальные аналоги:
stale policy in agents
outdated assumptions
incorrect step persistence (привет RV Service Desk)
 Мы показываем:
это не игра, а абстракция реального бага
🔥 Если нет:

→ это академическая игрушка

📊 7. Metric Soundness
❌ Судья атакует:

“Ваши метрики можно обмануть.”

Проверка:
 CDL не ловит случайные флуктуации
 AHL не ломается на шуме
 PR не коррелирует тупо с error rate
 PCS реально измеряет стабильность
🔥 Красный флаг:

если все метрики сильно коррелируют → они бесполезны

🧨 8. Goodhart Resistance
❌ Судья атакует:

“Модель просто оптимизируется под ваши метрики.”

Проверка:
 Нет одной доминирующей метрики
 Есть trade-offs:
быстро адаптироваться vs не шуметь
 Нельзя “накрутить score” одной стратегией
🧠 9. Minimal vs Toy (самый тонкий момент)
❌ Судья атакует:

“Это слишком просто.”

Проверка:

 Мы можем объяснить:

почему минимальность = контроль, а не упрощение

 Есть escalation:
shift → conditional → stateful
 Есть roadmap расширения
🧪 10. Baseline Differentiation
❌ Судья атакует:

“Все модели показывают одинаковый результат.”

Проверка:
 Random agent → провал
 Static heuristic → высокий PCM, плохой CDL/PR
 Adaptive agent → лучший overall
🔥 Если этого нет:

→ benchmark не работает

⚙️ 11. Reproducibility
❌ Судья атакует:

“Я не могу это запустить.”

Проверка:
 один config → один результат
 seed-controlled generation
 offline runnable
 без внешних API
🧨 12. Novelty Defense
❌ Судья атакует:

“Это уже было.”

Проверка:
 Мы НЕ говорим “мы первые”
 Мы говорим:
что есть (lifelong, agent evals)
чего нет (наш точный фокус)
Наш тезис должен звучать так:
We isolate latent mid-episode rule revision as a first-class evaluation target,
and explicitly measure detection latency, policy update, and perseveration.
🧩 13. Simplicity Trap (самый опасный)
❌ Судья думает:

“Выглядит просто → значит слабо”

Как защититься:
 показать:
сложное поведение на простой среде
 показать:
разные failure modes
 показать:
почему усложнение не добавляет signal
🧠 Финальный тест (самый честный)

Если судья спросит:

“Почему ваш benchmark лучше, чем просто дать модели больше задач?”

У нас должен быть ответ:

👉 Потому что:

задачи меряют что модель может
мы меряем как модель меняет своё поведение, когда она ошиблась